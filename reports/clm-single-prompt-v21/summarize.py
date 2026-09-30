"""Summarize completed attempts; distinguish encoder work from cache hits."""
import argparse
import collections
import csv
import json
import statistics
from pathlib import Path

def quantiles(values):
    if not values:return {'count':0,'p50_ms':None,'p95_ms':None}
    values=sorted(values)
    return {'count':len(values),'p50_ms':statistics.median(values),'p95_ms':values[int(.95*(len(values)-1))]}

p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root
manifest=json.loads((root/'manifest.json').read_text())
design_note=('Fixed prompt with empty global memory and no S2 updates; repeated identical seed/checkpoint, not a generalization estimate.'
             if manifest.get('protocol')=='clm-fixed-no-memory-v1' else
             'Adaptive prompt sequence at fixed seed, not independent trials of one frozen policy.')
if manifest.get('protocol')=='clm-single-prompt-v1':
    design_note=('One prompt per attempt, no notes or note clock, frozen candidate descriptions. '
                 +('Failure-only reflection is enabled. ' if manifest['reflection_enabled'] else 'S2 is disabled. ')
                 +'Repeated identical seed/checkpoint, not a generalization estimate.')
out=[];all_lat=[];encoder=[];cached=[]
for d in sorted((root/'attempts').iterdir()):
    if not (d/'summary.json').exists():continue
    s=json.loads((d/'summary.json').read_text());counts=collections.Counter();local_encoding=[];local_cached=[]
    for p in sorted((d/'decisions').glob('*.json')):
        row=json.loads(p.read_text());counts[row['selected_action']]+=1;lat=row['latency_ms'];all_lat.append(lat)
        if row['response']['usage']['input_tokens']:
            encoder.append(lat);local_encoding.append(lat)
        else:cached.append(lat);local_cached.append(lat)
    s.update(selected_action_counts=dict(counts),dominant_action=counts.most_common(1)[0][0],
             action_types=len(counts),encoder_work=quantiles(local_encoding),fully_cached=quantiles(local_cached))
    out.append(s)
result={'attempts_completed':len(out),'clears':sum(s['native_flag_get'] for s in out),
        'outcomes':dict(collections.Counter(s['outcome'] for s in out)),
        'best':max(out,key=lambda s:s['max_x']) if out else None,
        'first_clear':next((s for s in out if s['native_flag_get']),None),
        'native_frames':sum(s['frames'] for s in out),'decisions':len(all_lat),
        'automatic_release_decisions':sum(s['automatic_releases'] for s in out),
        'attempt_wall_s':sum(s['attempt_wall_s'] for s in out),
        'latency':{'all':quantiles(all_lat),'encoder_work':quantiles(encoder),'fully_cached':quantiles(cached)},
        'attempts':out,'note':design_note+' Encoder work may encode a new state, candidate description, or both.'}
(root/'audit/metrics.json').write_text(json.dumps(result,indent=2)+'\n')
with (root/'audit/attempts.csv').open('w',newline='') as f:
    fields=['attempt_id','program_version','outcome','max_x','frames','decisions','attempt_wall_s','automatic_releases','dominant_action','action_types','p50_ms','p95_ms']
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(out)
print(json.dumps({k:v for k,v in result.items() if k not in ('attempts','best','first_clear')},indent=2))
