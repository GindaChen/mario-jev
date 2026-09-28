'use strict';
(async () => {
  const $ = id => document.getElementById(id);
  const el = (tag, text, cls) => { const n=document.createElement(tag); if(text!==undefined)n.textContent=text; if(cls)n.className=cls; return n; };
  const link = (text, href) => { const n=el('a',text);n.href=href;return n; };
  const names={cleared:'Cleared',failed:'Gameplay failure',api_error:'API error',interrupted:'Worker restart'};
  let research, feed, selected=-1, mode='full';
  const video=$('campaign-video');
  function chooseMode(next, seconds=0) {
    const url=next==='full'?feed.artifacts.replay_url:feed.artifacts.clears_url;
    if(!url)return;
    mode=next;
    $('chapter-label').textContent=next==='full'?'Choose any attempt below to jump to its replay chapter.':'Compilation begins with the successful 1-1 attempt; failed attempts are omitted.';
    $('watch-full').setAttribute('aria-pressed',String(mode==='full'));
    $('watch-clears').setAttribute('aria-pressed',String(mode==='clears'));
    $('watch-label').textContent=mode==='full'?'Chronological replay · all attempts':'Successful stages · STITCHED';
    $('watch-description').textContent=mode==='full'?'All 62 attempts in recorded order, including failures and stage loads. This is a sequence of stage runs, not one uninterrupted clear.':'An edited compilation of the 32 successful stage attempts. Failed attempts are omitted. Stage and original attempt numbers remain visible.';
    if(video.getAttribute('src')!==url) {video.src=url;video.addEventListener('loadedmetadata',()=>{video.currentTime=seconds;},{once:true});video.load();}
    else video.currentTime=seconds;
  }
  function inspect(index) {
    selected=index;const r=research.attempts[index];chooseMode('full',r.seconds);
    $('chapter-label').textContent=`Attempt ${index+1} of 62 · Stage ${r.stage} / try ${r.attempt} · ${names[r.result]}`;
    $('attempt-inspector').hidden=false;$('inspect-title').textContent=`Stage ${r.stage} · attempt ${r.attempt}`;
    $('inspect-result').textContent=`${r.detail} ${r.decisions.toLocaleString()} decisions. ${r.clear_count}/32 cumulative clears.`;
    $('inspect-request').textContent=r.first_request?JSON.stringify(r.first_request,null,2):'This legacy-policy attempt uses a different diagnostics shape. The complete trace and profile are preserved in the audit download.';
    renderAttempts();$('watch').scrollIntoView({behavior:'smooth',block:'start'});
  }
  function renderAttempts() {
    const stage=$('attempt-stage').value,outcome=$('attempt-outcome').value;
    const strip=document.createDocumentFragment(),body=document.createDocumentFragment();let shown=0;
    research.attempts.forEach((r,i)=>{
      if(stage!=='all'&&r.stage!==stage||outcome!=='all'&&r.result!==outcome)return;
      shown++;
      const b=el('button',r.stage,`${r.result}${selected===i?' selected':''}`);b.type='button';b.title=`#${i+1}: ${r.stage} try ${r.attempt} · ${names[r.result]}`;b.setAttribute('aria-label',b.title);b.addEventListener('click',()=>inspect(i));strip.append(b);
      const tr=el('tr',undefined,selected===i?'selected':'');
      [i+1,`${r.stage} / ${r.attempt}`,names[r.result],`${r.clear_count} / 32`,r.decisions.toLocaleString()].forEach(v=>tr.append(el('td',v)));
      const prompt=el('td');prompt.append(link(r.profile,r.profile_url));tr.append(prompt);
      const td=el('td'),watch=el('button','Watch ↗','watch-attempt');watch.type='button';watch.addEventListener('click',()=>inspect(i));td.append(watch);tr.append(td);body.append(tr);
    });
    $('attempt-strip').replaceChildren(strip);$('attempt-rows').replaceChildren(body);$('attempt-count').textContent=`Showing ${shown} of ${research.attempts.length} attempts · chronological order`;
  }
  function renderStories() {
    for(const r of research.revisions) {
      const article=el('article',undefined,'revision-card');article.append(el('p',`WORLD ${r.stage} / REVISION ENTERS AT ATTEMPT ${r.attempt}`,'eyebrow'),el('h3',r.title));
      const grid=el('div',undefined,'revision-grid');
      for(const [title,copy] of [['Observed failure',r.failure],['Prompt revision',r.change],['Measured outcome',r.outcome]]){const p=el('p');p.append(el('strong',title),document.createTextNode(copy));grid.append(p);}article.append(grid);
      const details=el('details');details.append(el('summary',`Exact prompt changes · ${r.diffs.length} changed fields / notes`));
      for(const d of r.diffs){details.append(el('p',d.path,'diff-path'));const pair=el('div',undefined,'prompt-diff');for(const side of ['before','after']){const col=el('div');col.append(el('h4',side.toUpperCase()),el('pre',JSON.stringify(d[side],null,2)));pair.append(col);}details.append(pair);}article.append(details);
      const links=el('div',undefined,'revision-links');links.append(link('Previous prompt JSON',r.before_url),link('Revised prompt JSON',r.after_url));
      const b=el('button','Watch the revised attempt','watch-attempt');b.type='button';b.addEventListener('click',()=>inspect(research.attempts.findIndex(a=>a.stage===r.stage&&a.attempt===r.attempt)));links.append(b);article.append(links);$('revision-stories').append(article);
    }
    $('unused-stories').append(el('strong','Prepared does not mean used'));
    for(const r of research.unused_candidates)$('unused-stories').append(el('p',`${r.stage} — ${r.text}`));
  }
  try {
    const responses=await Promise.all(['/data/campaign-research.json','/data/campaign.json'].map(url=>fetch(url,{cache:'no-store'})));
    if(responses.some(r=>!r.ok))throw Error('Research records unavailable');
    [research,feed]=await Promise.all(responses.map(r=>r.json()));
    if(research.campaign_id!==feed.campaign_id||feed.status!=='completed'||!feed.artifacts?.replay_url)throw Error('Verified replay publication is not ready for this campaign.');
    if(!/^\/data\/campaign-final\/[A-Za-z0-9_-]+\/campaign-replay\.mp4$/.test(feed.artifacts.replay_url))throw Error('Invalid replay path');
    if(feed.artifacts.clears_url!==feed.artifacts.replay_url.replace('campaign-replay.mp4','campaign-clears.mp4'))throw Error('Invalid compilation path');
    for(const stage of [...new Set(research.attempts.map(r=>r.stage))]) {const o=el('option',stage);o.value=stage;$('attempt-stage').append(o);}
    $('attempt-stage').addEventListener('change',renderAttempts);$('attempt-outcome').addEventListener('change',renderAttempts);
    $('watch-full').addEventListener('click',()=>{selected=-1;chooseMode('full');renderAttempts();});$('watch-clears').addEventListener('click',()=>{selected=-1;chooseMode('clears');renderAttempts();});
    document.dispatchEvent(new CustomEvent('campaign-history-ready', {detail:research}));
    chooseMode('full');renderStories();renderAttempts();
  } catch(error) {$('chapter-label').textContent=error.message;$('attempt-count').textContent='Could not load the frozen research record. The runner feed and audit links below remain available.';}
})();
