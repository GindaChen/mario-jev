"""Build a frozen, public research view from the completed campaign evidence."""
import json, hashlib, argparse
from collections import Counter
from pathlib import Path
BASE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--campaign-root',type=Path,default=BASE.parent/'runs/overnight-campaign')
ROOT=parser.parse_args().campaign_root
def load(p): return json.loads(p.read_text())
status=load(ROOT/'status.json'); verification=load(ROOT/'verification.json')
assert status['status']=='completed' and verification['replay_verified']
rows=[]; events=[]; current=None; frame=0; wins=0; source=None
for line in (ROOT/'trajectory.jsonl').open():
 r=json.loads(line)
 if r['type']=='config': source=r['source_sha256']
 if r['type']=='event':
  events.append({k:r[k] for k in ['at','kind','stage','attempt','message'] if k in r})
  if r['kind']=='stage_start':
   profile=load(ROOT/r['profile']); name=Path(r['profile']).name
   assert hashlib.sha256((ROOT/r['profile']).read_bytes()).hexdigest()==r['profile_sha256']
   (BASE/'public/data/campaign-research/profiles'/name).write_bytes((ROOT/r['profile']).read_bytes())
   current=dict(stage=r['stage'],attempt=r['attempt'],at=r['at'],profile=profile.get('name','default'),profile_url='/data/campaign-research/profiles/'+name,profile_sha256=r['profile_sha256'],source_sha256=source,seconds=frame/60,decisions=0,result='interrupted',detail='Worker restarted before this attempt completed.',clear_count=wins)
   rows.append(current);frame+=60
  elif r['kind'] in ['stage_clear','stage_failure','error'] and current:
   current['result']={'stage_clear':'cleared','stage_failure':'failed','error':'api_error'}[r['kind']];current['detail']=r['message'];current['end_at']=r['at']
   if r['kind']=='stage_clear': wins+=1
   current['clear_count']=wins
 elif r['type']=='decision':
  frame+=r['frames_executed']; current['decisions']+=1;current['final_x']=r['result']['x']
  if 'first_request' not in current and isinstance(r['controller'].get('backend_diagnostics'),list):
   current['first_request']=r['controller']['backend_diagnostics'][-1].get('request')
assert len(rows)==62 and wins==32 and sum(r['decisions'] for r in rows)==22793
assert Counter(r['result'] for r in rows)==dict(cleared=32,failed=27,api_error=2,interrupted=1)
assert frame==verification['replays']['full']['verification']['video_frames']
stories=[
 ('1-1',3,'Fit the request into context','The first two attempts ended with API errors; full observations exceeded the serving context limit.','Switched the request to minimal observations.','The minimal profile cleared on attempt 5, after two gameplay failures.','observation'),
 ('2-1',6,'Make the landing instruction specific','At x1518, the long request selected right_run while Mario was rising; the saved winner braked with left_jump.','Replaced the local instruction and supplied only motion: rising → left_jump; otherwise → right_run.','Attempt 6 cleared the stage.','early-enemy-landing'),
 ('6-2',4,'Test a new route out of the pipe trap','Attempts 1–3 stalled at x1378 after jumping too early from a higher pipe.','Tried dropping to the intermediate step, braking, waiting, then jumping. Physics probes informed the prompt; those probes do not count as model clears.','Attempts 4–5 got farther but failed. This revision was not retained as the successful policy.',None),
 ('6-2',6,'Recover the earlier landing choice','The first divergence was at x1141: the same original request produced a left/wait tie instead of the historical wait.','Returned to the original profile and added a narrow motion-only landing instruction: release controls when falling.','Attempt 6 cleared. All 518 actions, frame counts, and Mario states matched the historical winner.','campaign-landing-release'),
 ('7-2',5,'Clarify the water-exit stroke','Attempts 1–4 died near x2998 after missing an upward stroke at the exit shelf.','Added a narrow motion-only note around x2900: stroke when grounded or rising; release when falling.','Attempt 5 cleared.',None),
]
revisions=[]
for stage,attempt,title,failure,change,outcome,note in stories:
 row=next(r for r in rows if r['stage']==stage and r['attempt']==attempt)
 prior=next(r for r in rows if r['stage']==stage and r['attempt']==attempt-1)
 before=load(ROOT/'profiles'/Path(prior['profile_url']).name); after=load(ROOT/'profiles'/Path(row['profile_url']).name)
 oldnotes={n['id']:n for n in before.get('memory_notes',[])}; newnotes={n['id']:n for n in after.get('memory_notes',[])}
 diffs=[dict(path='memory_notes.'+k,before=oldnotes.get(k),after=newnotes.get(k)) for k in sorted(oldnotes.keys()|newnotes.keys()) if oldnotes.get(k)!=newnotes.get(k)]
 for k in sorted(before.keys()|after.keys()):
  if k not in ['name','memory_notes'] and before.get(k)!=after.get(k):diffs.append(dict(path=k,before=before.get(k),after=after.get(k)))
 revisions.append(dict(stage=stage,attempt=attempt,title=title,failure=failure,change=change,outcome=outcome,diffs=diffs,before_url=prior['profile_url'],after_url=row['profile_url']))
result=dict(campaign_id=status['campaign_id'],trace_sha256=verification['integrity']['trace_sha256'],started_at=status['started_at'],finished_at=status['updated_at'],attempts=rows,events=events,revisions=revisions,unused_candidates=[dict(stage='1-3',text='A grounded-only candidate was prepared, but attempt 5 cleared using the original profile before that candidate was needed.'),dict(stage='8-4',text='Four attempts failed. A focused wait candidate was prepared, but attempt 5 cleared with the original r82 profile. The candidate did not cause this success.')],scope='This is the new sequential campaign, initialized from prior stage-specific winners. Earlier independent-stage optimization is a separate experiment. Reflections below are retrospective summaries grounded in saved traces and profile changes, not a private reasoning transcript.')
(BASE/'public/data/campaign-research.json').write_text(json.dumps(result,indent=2)+'\n')
print('Built',len(rows),'attempts,',len(events),'events,',len(revisions),'revision stories')
