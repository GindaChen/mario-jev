"""Read-only experiment indexer. Publishes only allowlisted gameplay fields."""
import hashlib,json,os,re,time,threading,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
HARNESS=Path(os.environ.get('MARIO_HARNESS','/home/juc049/projects/mario-amd/harness'))
CACHE={}
MANIFEST_CACHE={}
PROFILE_FIELDS=("instructions","global_instructions","criteria","memory_notes","thresholds","inference","mode","questions","one_frame_rearm","observation_style","compact_state","reflection_start_x","units","route_geometry","route_displacement","route_minimal","route_floor","hazard_pixels","enemy_vertical","movement_enemies")

def provenance(path):
    manifest=path.parent.parent/"manifest.json"
    if not manifest.exists():return {}
    key=manifest.stat().st_mtime_ns
    if manifest not in MANIFEST_CACHE or MANIFEST_CACHE[manifest][0]!=key:
        try:
            data=json.loads(manifest.read_text())
            entries={Path(a.get("directory","")).name:a for a in data.get("attempts",[])}
            MANIFEST_CACHE[manifest]=(key,entries)
        except (ValueError,OSError):return {}
    return MANIFEST_CACHE[manifest][1].get(path.parent.name,{})

def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False));tmp.replace(path)

def records(path):
    with path.open() as f:
        for line in f:
            try: yield json.loads(line)
            except (ValueError,TypeError): continue

def read_run(path):
    st=path.stat(); key=(st.st_mtime_ns,st.st_size)
    if path in CACHE and CACHE[path][0]==key:return CACHE[path][1]
    it=iter(records(path));c=next(it,{})
    if c.get('policy')!='djev' or not re.fullmatch(r'SuperMarioBros-[1-8]-[1-4]-v0',c.get('env','')):return None
    if c.get('resume_from') or c.get('fresh_start') is False:return None
    stage='-'.join(c['env'].split('-')[1:3]);rid=path.stem
    # Filename timestamps supply immutable start time; mtime supplies last activity.
    try:started=datetime.strptime(rid,'%Y%m%dT%H%M%S%fZ').replace(tzinfo=timezone.utc).timestamp()
    except ValueError:started=st.st_mtime
    summary=None;last={};count=0;latencies=[];notes={};start_x=None;furthest_x=0;example_question=None
    for d in it:
        if d.get('type')=='summary':summary=d
        elif d.get('type')=='decision':
            last=d;count+=1
            if start_x is None:start_x=d.get("state",{}).get("mario",{}).get("x")
            furthest_x=max(furthest_x,d.get("result",{}).get("x",0))
            if example_question is None:
                for diag in d.get("backend_diagnostics",[]):
                    if not isinstance(diag,dict):continue
                    q=diag.get("request",{}).get("questions",{}).get("action")
                    if q:example_question={k:q[k] for k in ("instructions","criteria") if k in q};break
            if isinstance(d.get('latency_ms'),(int,float)):latencies.append(d['latency_ms'])
            for note in d.get('active_memory_notes',[]):
                nid=note.get('id',note.get('instructions',''));notes[nid]={k:note[k] for k in ('id','min_x','max_x','instructions','criteria') if k in note}
    profile_path=path.parent/'profile.json';profile={}
    if profile_path.exists():
        try:profile=json.loads(profile_path.read_text())
        except ValueError:pass
    prov=provenance(path)
    prompt_config={k:profile[k] for k in PROFILE_FIELDS if k in profile}
    if not prompt_config and example_question:
        prompt_config=dict(example_question);prompt_config['memory_notes']=list(notes.values())
    info={'id':rid,'stage':stage,'started_at':started,'updated_at':st.st_mtime,
          'profile':last.get('profile',Path(c.get('jev_profile') or 'default').stem),
          'model':'DJev','decisions':count,'completed':bool(summary and summary.get('completed')),
          'finished':bool(summary),'stop_reason':summary.get('stop_reason') if summary else None,
          'max_x':(summary or {}).get('max_x',furthest_x),'start_x':start_x,
          'source_sha256':prov.get('source_sha256'),'batch_attempt':prov.get('id'),
          'prompt_config_complete':bool(profile),'policy_sha256':hashlib.sha256(json.dumps(prompt_config,sort_keys=True).encode()).hexdigest(),
          'last_action':last.get('action'),'latency_ms':round(latencies[-1],1) if latencies else None,
          'median_latency_ms':round(sorted(latencies)[len(latencies)//2],1) if latencies else None,
          'profile_sha256':last.get('profile_sha256',c.get('jev_profile_sha256')),
          'trace_sha256':hashlib.sha256(path.read_bytes()).hexdigest() if summary else None,
          'seed':c.get('seed'),'fresh_start':True,
          'series':'reflection-100' if 'djev-reflection-100' in path.parts else 'stage-campaign' if 'stages' in path.parts else 'early-baseline',
          'detail_url':f'/data/runs/{rid}.json'}
    detail={**info,'instructions':profile.get('instructions'),'criteria':profile.get('criteria'),
            'prompt_config':prompt_config,'example_logged_question':example_question,
            'prompt_evidence':'profile snapshot' if profile else 'logged question and activated notes only; full profile not archived here',
            'memory_notes':profile.get('memory_notes',list(notes.values())),
            'last_observation':last.get('state',{}).get('mario',{}),
            'selected_action':last.get('decisions',{}).get('selected_action'),
            'note':'Public summary of recorded gameplay. Model calls pause the emulator. No private chat or credentials are published.'}
    write_json(PUBLIC/'data/runs'/f'{rid}.json',detail)
    CACHE[path]=(key,info)
    return info

def collect():
    paths=list((HARNESS/'runs/stages').glob('*/*/*.jsonl'))+list((HARNESS/'runs/stages').glob('*/*/*/*.jsonl'))
    paths+=list((HARNESS/'runs/stage-play').glob('**/*.jsonl'))
    paths+=list((HARNESS/'runs/djev-reflection-100').glob('*/*.jsonl'))
    paths+=[HARNESS/'runs/20260926T221401248810Z.jsonl']
    runs=[];sources={}
    for path in sorted(set(paths)):
        if not path.exists():continue
        r=read_run(path)
        if r:runs.append(dict(r));sources[r['id']]=path
    now=time.time()
    for r in runs:r['status']='cleared' if r['completed'] else 'finished' if r['finished'] else 'running' if now-r['updated_at']<180 else 'incomplete'
    stages=[]
    for w in range(1,9):
        for n in range(1,5):
            key=f'{w}-{n}';rs=sorted([r for r in runs if r['stage']==key],key=lambda r:r['started_at']);wins=[r for r in rs if r['completed']]
            live=[r for r in rs if r['status']=='running'];done=[r for r in rs if r['finished']]
            status='cleared' if wins else 'running' if live else 'attempted' if rs else 'untested'
            videos=PUBLIC/'media'/f'{key}.mp4';poster=PUBLIC/'media'/f'{key}.jpg'
            s={'id':key,'world':w,'stage':n,'status':status,'attempts':len(rs),'finished':len(done),'wins':len(wins),'max_x':max((r['max_x'] or 0 for r in rs),default=0),'running':len(live),'latest':rs[-1]['id'] if rs else None,'first_win':wins[0]['id'] if wins else None,'finish_x':wins[0]['max_x'] if wins else None,
               'distance_note':'Distance is a spatial proxy, not a guarantee of stage completion. Pipes, transitions, looping mazes and falling can make x misleading.','video':f'/media/{key}.mp4' if videos.exists() else None,'poster':f'/media/{key}.jpg' if poster.exists() else None}
            if key=='1-2':
                s['validation']={'wins':20,'attempts':20,'description':'Two frozen profiles, 10 runs each. Same level and reset seed.'};s['status']='validated' if len(wins)>=20 else status
            if key=='1-3' and len(wins)>=8:
                s['validation']={'wins':6,'attempts':6,'description':'Frozen r24 and r25, 3 repetitions each. Same reset seed; stage-specific coaching.'}
                s['status']='validated'
            stages.append(s)
    runs.sort(key=lambda r:r['started_at'],reverse=True)
    doc={'schema_version':2,'generated_at':now,'refresh_seconds':15,'title':'Mario / Game Lab','stages':stages,'runs':runs,'cleared_stages':sum(s['wins']>0 for s in stages),'total_stages':32,'total_attempts':len(runs),'total_wins':sum(r['completed'] for r in runs),'active_runs':sum(r['status']=='running' for r in runs),'latest_activity':max((r['updated_at'] for r in runs),default=None),'limitations':['Each stage starts separately. This is not a continuous full-game clear.','Stage-specific prompts and reflection notes are allowed. Model weights are unchanged.','The emulator pauses for inference; videos are replays at 60 game frames per second.','A first clear is not a reliability estimate. The 1-2 validation uses a fixed reset scenario.']}
    write_json(PUBLIC/'data/mario.json',doc)
    return doc,sources

def replay_worker():
    """One CPU-only first-clear export at a time, entirely outside inference processes."""
    while True:
        try:
            data=json.loads((PUBLIC/'data/mario.json').read_text())
            for s in data['stages']:
                rid=s['first_win'];out=PUBLIC/'media'/f"{s['id']}.mp4"
                if not rid or out.exists():continue
                matches=list((HARNESS/'runs').glob(f'**/{rid}.jsonl'))
                if not matches:continue
                tmp=out.with_name(out.stem+'.building.mp4')
                tmp.unlink(missing_ok=True)
                result=subprocess.run([str(HARNESS/'.venv/bin/python'),str(HARNESS/'scripts/export_replay.py'),str(matches[0]),str(tmp)],cwd=HARNESS,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1'})
                if result.returncode==0:
                    tmp.replace(out)
                    subprocess.run(['ffmpeg','-v','error','-y','-ss','2','-i',str(out),'-frames:v','1',str(out.with_suffix('.jpg'))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
        except Exception as error: print('Replay export retry:',type(error).__name__,flush=True)
        time.sleep(45)

def loop():
    while True:
        try:collect()
        except Exception as error:print('Publisher retry:',type(error).__name__,str(error)[:200],flush=True)
        time.sleep(15)

if __name__=='__main__':
    collect()
    if '--once' not in __import__('sys').argv:
        threading.Thread(target=replay_worker,daemon=True).start();loop()
