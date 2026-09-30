"""Audit single-prompt invariants using saved programs and every actual request."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def verify(root):
    manifest=read(root/'manifest.json')
    assert manifest['protocol']=='clm-single-prompt-v1'
    source=read(root/'frozen/source-program.json')
    initial=read(root/'programs/v0000/program.json')
    assert initial=={'instructions':source['instructions']+'\n'+source['memory'], 'criteria':source['criteria']}
    count=0; attempts=[]; hashes=set()
    for folder in sorted((root/'attempts').iterdir()):
        summary=read(folder/'summary.json')
        version=summary['program_version']
        program=read(root/f'programs/v{version:04}/program.json')
        assert set(program)=={'instructions','criteria'}
        assert program['criteria']==source['criteria']
        prompt_hash=hashlib.sha256(program['instructions'].encode()).hexdigest()
        hashes.add(prompt_hash)
        profile=read(root/f'programs/v{version:04}/profile.json')
        assert set(profile)=={'name','mode','single_prompt','one_frame_rearm','instructions','criteria'}
        assert profile['single_prompt'] and profile['instructions']==program['instructions']
        rows=sorted((folder/'decisions').glob('*.json'))
        for path in rows:
            row=read(path); request=row['request']
            assert row['program_version']==version
            assert request['questions']=={'action':{'type':'choice',**program}}
            assert 'note_elapsed_frames' not in request['state']
            count+=1
        assert len(rows)==summary['decisions']
        attempts.append({'attempt_id':summary['attempt_id'],'program_version':version,
                         'instructions_sha256':prompt_hash,'decisions_checked':len(rows)})
    agent_runs=len(list((root/'workspaces').iterdir()))
    result={'passed':True,'decisions_checked':count,'attempts_checked':len(attempts),
            'distinct_prompt_hashes':sorted(hashes),'agent_workspaces':agent_runs,
            'reflection_enabled':manifest['reflection_enabled'],'attempts':attempts,
            'checks':['Initial prompt exactly equals source instructions + newline + source memory',
                      'Each attempt has exactly one immutable instructions string',
                      'All eight candidate descriptions remain frozen',
                      'No memory fields or note/router objects in any program/profile',
                      'No note_elapsed_frames in any actual model request']}
    (root/'audit/single-prompt-integrity.json').write_text(json.dumps(result,indent=2)+'\n')
    return {k:v for k,v in result.items() if k!='attempts'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',type=Path)
    print(json.dumps(verify(parser.parse_args().root),indent=2))
