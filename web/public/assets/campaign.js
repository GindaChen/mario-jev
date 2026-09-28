'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const stages = Array.from({length: 8}, (_, w) => Array.from({length: 4}, (_, s) => `${w + 1}-${s + 1}`)).flat();
  const count = value => Number.isFinite(Number(value)) ? Math.max(0, Number(value)).toLocaleString() : '0';
  const label = value => typeof value === 'string' ? value.replaceAll('_', ' ') : '';
  const date = value => value && Number.isFinite(Date.parse(value)) ? new Date(value) : null;
  const age = value => date(value) ? Math.max(0, (Date.now() - date(value).getTime()) / 1000) : null;
  const since = seconds => seconds === null ? 'unknown' : seconds < 2 ? 'just now' : seconds < 60 ? `${Math.floor(seconds)}s ago` : seconds < 3600 ? `${Math.floor(seconds / 60)}m ago` : `${Math.floor(seconds / 3600)}h ago`;
  let data = null, selected = null, manuallySelected = false, fetching = false, fetchError = false, frameKey = '', eventKey = '';
  let frozenHistory = null;
  document.addEventListener('campaign-history-ready', event => { frozenHistory = event.detail; if (data) renderEvents(); });
  const tiles = new Map();
  for (let world = 1; world <= 8; world++) {
    const heading = document.createElement('span'); heading.className = 'world-label'; heading.textContent = `W${world}`; $('stage-grid').append(heading);
    for (let level = 1; level <= 4; level++) {
      const stage = `${world}-${level}`, button = document.createElement('button'); button.type = 'button'; button.className = 'stage-tile';
      const title = document.createElement('strong'), attempts = document.createElement('small'); title.textContent = stage; attempts.textContent = 'Pending'; button.append(title, attempts);
      button.addEventListener('click', () => { selected = stage; manuallySelected = true; renderStages(); });
      tiles.set(stage, {button, attempts}); $('stage-grid').append(button);
    }
  }
  function renderStages() {
    if (!data) return;
    if (!manuallySelected) selected = data.current_stage || stages[0];
    for (const stage of stages) {
      const result = data.stage_results?.[stage] || {}, current = stage === data.current_stage, cleared = result.status === 'cleared', tile = tiles.get(stage);
      tile.button.className = `stage-tile${cleared ? ' cleared' : current ? ' current' : ''}${stage === selected ? ' selected' : ''}`;
      tile.button.setAttribute('aria-pressed', String(stage === selected));
      const state = cleared ? 'Cleared' : current ? 'Current' : 'Pending';
      tile.button.setAttribute('aria-label', `World ${stage}, ${state}, ${count(result.attempts)} attempts, ${count(result.retries)} retries`);
      tile.attempts.textContent = result.attempts ? `${count(result.attempts)} ${result.attempts === 1 ? 'attempt' : 'attempts'}` : state;
    }
    const result = data.stage_results?.[selected] || {}, state = result.status === 'cleared' ? 'Recorded clear' : selected === data.current_stage ? 'Current stage' : 'Pending';
    $('selected-stage').textContent = `World ${selected} · ${state}`;
    $('selected-detail').textContent = `${count(result.attempts)} attempts · ${count(result.retries)} stage retries · ${count(result.checkpoint_retries)} checkpoint reloads${date(result.completed_at) ? ` · cleared ${date(result.completed_at).toLocaleTimeString()}` : ''}`;
    $('research-link').href = `/mario/?stage=${encodeURIComponent(selected)}`;
  }
  function renderEvents() {
    const filter = $('event-filter').value;
    let events = frozenHistory?.campaign_id === data?.campaign_id ? frozenHistory.events : (Array.isArray(data?.event_log) ? data.event_log : []);
    if (filter === 'retries') events = events.filter(e => /restart|retry|checkpoint|death|stall|failure|error|reflection/i.test(`${e.kind} ${e.message}`));
    if (filter === 'stages') events = events.filter(e => /stage|clear|complet|start|mode/i.test(e.kind || ''));
    const key = JSON.stringify([filter, events]); if (eventKey === key) return; eventKey = key;
    const fragment = document.createDocumentFragment();
    for (const event of [...events].reverse()) {
      const li = document.createElement('li'), time = document.createElement('time'), stage = document.createElement('span'), copy = document.createElement('div'), detail = document.createElement('small');
      const at = date(event.at); time.textContent = at ? at.toLocaleTimeString([], {hour12: false}) : '—'; if (at) { time.dateTime = at.toISOString(); time.title = at.toLocaleString(); }
      stage.className = 'event-stage'; stage.textContent = event.stage || 'Campaign'; copy.className = 'event-copy'; copy.textContent = event.message || label(event.kind) || 'Campaign update';
      detail.textContent = `${label(event.kind)}${event.attempt ? ` · attempt ${event.attempt}` : ''}`; copy.append(detail); li.append(time, stage, copy); fragment.append(li);
    }
    if (!events.length) { const li = document.createElement('li'); li.className = 'empty-event'; li.textContent = filter === 'all' ? 'No campaign events yet.' : 'No matching events.'; fragment.append(li); }
    $('event-list').replaceChildren(fragment);
  }
  function refreshAges() {
    const updated = age(data?.updated_at), published = age(data?.published_at);
    const runnerStale = data?.status === 'running' && (updated === null || updated > 30);
    const publisherStale = data?.campaign_id && (published === null || published > 15);
    const stale = runnerStale || publisherStale;
    const state = label(data?.status || 'waiting_for_runner');
    $('feed-status').textContent = fetchError ? 'Connection interrupted' : stale ? 'Telemetry delayed' : state === 'running' ? 'Live campaign' : state.charAt(0).toUpperCase() + state.slice(1);
    $('feed-dot').className = `status-dot${fetchError || stale ? ' stale' : data?.status === 'running' ? ' live' : ''}`;
    const warning = fetchError ? 'Could not refresh the public feed. The last received snapshot remains visible.' : data?.feed_error || (publisherStale ? 'The public feed publisher is delayed. Showing its last snapshot.' : runnerStale ? `Runner telemetry is ${since(updated)}. Progress and the frame below may be stale.` : '');
    $('feed-warning').textContent = warning; $('feed-warning').hidden = !warning;
    $('updated-at').textContent = date(data?.updated_at) ? `Runner updated ${date(data.updated_at).toLocaleString()}` : 'Waiting for telemetry';
    $('frame-age').textContent = data?.frame ? `Frame ${since(age(data.frame.updated_at))}` : 'No frame yet';
  }
  function render() {
    const counts = data.counts || {}, current = data.current || {};
    $('cleared').replaceChildren(document.createTextNode(`${count(counts.cleared)} `)); const denominator = document.createElement('small'); denominator.textContent = '/ 32'; $('cleared').append(denominator);
    $('route-percent').textContent = `${count(counts.cleared)} / 32`;
    $('current-stage').textContent = data.current_stage || '—'; $('restarts').textContent = count(counts.restarts); $('checkpoint-retries').textContent = count(counts.checkpoint_retries); $('decisions').textContent = count(counts.total_decisions);
    const modes = {
      continuous: ['Continuous game', 'The game carries forward between stages. No separate stage environment has been loaded.'],
      continuous_with_recorded_restarts: ['Continuous game · recorded restarts', 'The campaign reports continuity with restarts. This is not an uninterrupted clear.'],
      stage_linked: ['Linked stages · recorded restarts', 'A separate stage environment has been loaded. Progress is a sequential route with resets, not an uninterrupted game.'],
      unknown: ['Waiting for the campaign runner', 'No new campaign progress has been reported yet. Historical stage wins are separate.']
    };
    const [name, detail] = modes[data.mode] || modes.unknown; $('mode-name').textContent = name; $('mode-detail').textContent = detail; $('mode-banner').className = `mode-banner${data.mode === 'stage_linked' || counts.restarts > 0 ? ' linked' : ''}`;
    $('attempt-label').textContent = data.current_stage ? `World ${data.current_stage} · attempt ${count(data.current_attempt)}` : 'No active attempt';
    $('action').textContent = current.action ? label(current.action) : '—'; $('latency').textContent = Number.isFinite(current.latency_ms) ? `${current.latency_ms.toFixed(1)} ms` : '—'; $('position').textContent = current.x ?? '—'; $('room').textContent = current.room ?? '—';
    $('campaign-id').textContent = data.campaign_id ? `Campaign ${data.campaign_id}` : 'Campaign not started';
    const frame = data.frame;
    if (frame?.url === '/data/campaign-frame.jpg') {
      const key = `${data.campaign_id}/${frame.updated_at}`;
      if (frameKey !== key) { frameKey = key; $('game-frame').src = `${frame.url}?v=${encodeURIComponent(frame.updated_at || '')}`; }
    } else { $('game-frame').hidden = true; $('frame-empty').hidden = false; frameKey = ''; }
    const artifacts = data.artifacts || {};
    const validFinal = data.status === 'completed' && counts.cleared === 32 && /^\/data\/campaign-final\/[A-Za-z0-9_-]+\/campaign-replay\.mp4$/.test(artifacts.replay_url || '') && /^\/data\/campaign-final\/[A-Za-z0-9_-]+\/verification\.json$/.test(artifacts.verification_url || '');
    $('final-artifacts').hidden = !validFinal;
    if (validFinal) { $('final-replay').href = artifacts.replay_url; $('final-audit').href = artifacts.verification_url; }
    else { $('final-replay').removeAttribute('href'); $('final-audit').removeAttribute('href'); }
    for (const [key, name, linkId, rowId] of [
      ['clears_url', 'campaign-clears.mp4', 'final-clears', 'final-clears-row'],
      ['audit_url', 'campaign-audit.tar.gz', 'final-archive', 'final-archive-row']
    ]) {
      const expected = validFinal ? artifacts.replay_url.replace('campaign-replay.mp4', name) : null;
      const show = validFinal && artifacts[key] === expected;
      $(rowId).hidden = !show;
      if (show) $(linkId).href = expected; else $(linkId).removeAttribute('href');
    }
    renderStages(); renderEvents(); refreshAges();
  }
  $('game-frame').addEventListener('load', () => { $('game-frame').hidden = false; $('frame-empty').hidden = true; });
  $('game-frame').addEventListener('error', () => { $('game-frame').hidden = true; $('frame-empty').hidden = false; $('frame-empty').querySelector('p').textContent = 'Frame temporarily unavailable'; });
  async function refresh() {
    if (fetching) return; fetching = true;
    try { const response = await fetch(`/data/campaign.json?t=${Date.now()}`, {cache: 'no-store'}); if (!response.ok) throw new Error('Feed unavailable'); const next = await response.json(); if (next.schema_version !== 1) throw new Error('Unknown schema'); if (data?.campaign_id !== next.campaign_id) { manuallySelected = false; frameKey = ''; } data = next; fetchError = false; render(); }
    catch { fetchError = true; refreshAges(); }
    finally { fetching = false; }
  }
  $('refresh').addEventListener('click', refresh); $('event-filter').addEventListener('change', renderEvents);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  refresh(); setInterval(refresh, 2000); setInterval(refreshAges, 1000);
})();
