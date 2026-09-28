"""Loopback-only public artifact server with byte-range video support."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,unquote
import os,re,json
from replay_service import ReplayService
REPLAYS=ReplayService()
PUBLIC=Path(__file__).resolve().parent/'public'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(PUBLIC),**kw)
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self'; frame-ancestors 'self'")
        self.send_header('Cache-Control','no-store' if '/data/' in self.path or '/api/' in self.path else 'public, max-age=60')
        super().end_headers()
    def do_GET(self):
        path=urlsplit(self.path).path
        if path.startswith('/api/replay/'):
            status,body=REPLAYS.request(path.removeprefix('/api/replay/'))
            encoded=json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        super().do_GET()
    def list_directory(self,path):self.send_error(404);return None
    def send_head(self):
        self.range_remaining=None
        urlpath=unquote(urlsplit(self.path).path)
        p=Path(self.translate_path(urlpath)).resolve()
        if not p.is_relative_to(PUBLIC) or any(part.startswith('.') for part in Path(urlpath).parts) or '.building.' in p.name:
            self.send_error(404);return None
        if self.headers.get('Range') and p.is_file():
            size=p.stat().st_size;m=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers['Range'])
            if not m:self.send_error(416);return None
            start=int(m[1]);end=min(int(m[2]) if m[2] else size-1,size-1)
            if start>end:self.send_error(416);return None
            f=p.open('rb');f.seek(start);self.range_remaining=end-start+1
            self.send_response(206);self.send_header('Content-Type',self.guess_type(str(p)))
            self.send_header('Content-Length',str(self.range_remaining));self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Accept-Ranges','bytes');self.end_headers();return f
        return super().send_head()
    def copyfile(self,source,output):
        try:
            if self.range_remaining is None:return super().copyfile(source,output)
            while self.range_remaining>0:
                data=source.read(min(65536,self.range_remaining))
                if not data:break
                output.write(data);self.range_remaining-=len(data)
        except (BrokenPipeError,ConnectionResetError):pass
    def log_message(self,*a):pass
if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('PORT','18480'))),Handler).serve_forever()
