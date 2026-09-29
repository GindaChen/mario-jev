"""Export a saved attempt at native 60 Hz without querying either model."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from mario_jev.policy import ACTIONS
from mario_jev.rsi_runtime.clm_pilot import make_env

p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('attempt',type=int);p.add_argument('output',type=Path)
a=p.parse_args();folder=a.root/f'attempts/{a.attempt:04}';summary=json.loads((folder/'summary.json').read_text())
env=make_env();env.reset(seed=0)
writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','256x240',
                         '-framerate','60','-i','pipe:0','-an','-vf','scale=512:480:flags=neighbor',
                         '-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],stdin=subprocess.PIPE)
count=0
try:
    for path in sorted((folder/'decisions').glob('*.json')):
        r=json.loads(path.read_text())
        assert hashlib.sha256(bytes(env.unwrapped.ram)).hexdigest()==r['before_ram_sha256']
        for _ in range(r['executed_frames']):
            env.step(list(ACTIONS).index(r['action']))
            writer.stdin.write(env.unwrapped.screen.copy().tobytes());count+=1
        assert hashlib.sha256(bytes(env.unwrapped.ram)).hexdigest()==r['after_ram_sha256']
    assert count==summary['frames']
finally:
    writer.stdin.close();code=writer.wait(timeout=60);env.close()
assert code==0
print(json.dumps({'attempt':a.attempt,'frames':count,'fps':60,'duration_s':count/60,'output':str(a.output),'verified':True}))
