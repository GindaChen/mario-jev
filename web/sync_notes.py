"""Publish only the campaign's explicit reflection reports; never chat transcripts."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parent
REPO=Path('/Users/jundac/Projects/ambient/research/mario-jev')
notes=[]
for path in sorted((REPO/'reports/stages').glob('*/reflection.md')):
    stage=path.parent.name
    if not re.fullmatch('[1-8]-[1-4]',stage):continue
    body=path.read_text()
    body=re.sub(r'/Users/[^\s`)\]]+|/home/[^\s`)\]]+','[local experiment path]',body)
    notes.append({'stage':stage,'text':body,'updated_at':path.stat().st_mtime,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
report=REPO/'deliverables/djev-reflection-100/analysis.md'
if report.exists():
    body=report.read_text();body=re.sub(r'/Users/[^\s`)\]]+|/home/[^\s`)\]]+','[local experiment path]',body)
    notes.append({'stage':'1-2','text':body,'updated_at':report.stat().st_mtime,'sha256':hashlib.sha256(report.read_bytes()).hexdigest()})
payload=json.dumps({'notes':notes},ensure_ascii=False).encode()
path=ROOT/'public/data/journal.json';path.parent.mkdir(parents=True,exist_ok=True)
if not path.exists() or path.read_bytes()!=payload:path.write_bytes(payload)
marker=ROOT/'.notes-published';digest=hashlib.sha256(payload).hexdigest()
if marker.exists() and marker.read_text()==digest:raise SystemExit(0)
subprocess.run(['/usr/bin/rsync','-az','-e','ssh -o BatchMode=yes -o ConnectTimeout=10',str(path),'amd:/home/juc049/projects/game-lab/public/data/journal.json'],check=True,timeout=45)
marker.write_text(digest)
