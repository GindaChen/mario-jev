const el=id=>document.getElementById(id);
async function refresh(){try{
 const r=await fetch('/data/continuous/status.json',{cache:'no-store'});if(!r.ok)throw Error('Feed unavailable');const d=await r.json();
 const age=(Date.now()-Date.parse(d.status==='running'?d.source_updated_at:d.updated_at))/1000;
 el('status').textContent=(age>90?'Feed stale · ':'')+d.status;
 el('updated').textContent='Updated '+new Date(d.updated_at).toLocaleString();
 const c=d.current,i=c.current||c.last_info||{};el('current').textContent=`Attempt ${c.attempt||'—'}\nStage ${c.stage||c.furthest_stage||'—'}\nDecisions ${c.decisions??'—'} · Frames ${c.frames??'—'}\nx ${i.x_pos??'—'} · Timer ${i.time??'—'}\nPower: ${i.status||'—'} · Score: ${i.score??'—'}`;
 el('budget').textContent=`${d.attempts.length} finished attempts / limit ${d.attempt_limit}. No new attempts after a clear or an error.`;
 el('attempts').replaceChildren();for(const a of d.attempts){const tr=document.createElement('tr');for(const v of [a.attempt,a.outcome,a.cleared.join(', ')||'None',a.furthest_stage,a.decisions,a.frames]){const td=document.createElement('td');td.textContent=v;tr.append(td)}el('attempts').append(tr)}
 el('prompt').textContent=d.prompt;el('hash').textContent='Frozen policy SHA-256: '+d.profile_sha256;
 if(d.has_frame)el('frame').src='/data/continuous/frame.jpg?t='+encodeURIComponent(d.updated_at);
}catch(e){el('status').textContent='Waiting for experiment feed';el('updated').textContent=e.message}}
refresh();setInterval(refresh,5000);
