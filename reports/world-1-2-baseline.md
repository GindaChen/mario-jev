# World 1-2: frozen-profile transfer test

2026-09-27, AMD physical GPU7. Same successful model checkpoints and profiles as1-1;
world1, stage2, seed123, frames4, default500-decision limit. No resume, retraining,
prompt edits, or scripted rescue. Models were tested concurrently; timings are
not isolated benchmarks.

| Model | Profile | Decisions | Max x | Result |
|---|---|---:|---:|---|
| Laya | laya/v9 |230|978|Stalled|
| OpenJev4 | modular/v10 |230|978|Stalled|
| Nimble | laya/v9 |175|1113|Died|

All requests and actions are saved locally and on AMD in `runs/amd-1-2-*`.
These runs show no successful transfer to1-2 yet. Laya and OpenJev repeatedly
failed to move beyond the same obstacle; their model-controlled jump sequences
were insufficient. Do not claim the models cannot solve1-2 after further work.

Watch the OpenJev attempt locally:

```sh
.venv/bin/mario-jev --replay runs/amd-1-2-openjev4/20260927T222545605491Z.jsonl
```

Run a fresh attempt on AMD:

```sh
cd /home/juc049/projects/mario-amd/harness
.venv/bin/mario-jev --policy modular --model openjev4 \
  --decision-url http://127.0.0.1:18824 \
  --decision-profile prompts/modular/v10.json \
  --world 1 --stage 2 --headless --log-dir runs/amd-1-2-openjev4
```
