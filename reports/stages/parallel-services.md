# AMD parallel DJev services

Provisioned three additional clones of the existing GPU7 deployment for the stage campaign. Existing GPU7 containers and other services were not restarted or changed.

| Physical GPU (rocm-smi) | PCI address | HIP ordinal | DJev API | Model API |
|---|---|---:|---|---|
| 4 | 0000:85:00.0 | 5 | http://127.0.0.1:18516 | http://127.0.0.1:18524 |
| 5 | 0000:95:00.0 | 7 | http://127.0.0.1:18517 | http://127.0.0.1:18525 |
| 6 | 0000:e5:00.0 | 6 | http://127.0.0.1:18518 | http://127.0.0.1:18526 |
| 7 (existing) | 0000:f5:00.0 | 4 | http://127.0.0.1:18515 | http://127.0.0.1:18514 |

Mapping was measured with hipDeviceGetPCIBusId and rocm-smi. Physical GPUs4–6 showed zero allocated VRAM before provisioning. Each new model container has its own HIP_VISIBLE_DEVICES ordinal and writable cache; model weights and adapter source are shared read-only. All ports bind localhost. No hosted API credentials were copied.

Pinned image: sha256:03a63c57bce6b7f45bd4845d306a73f037ff4877d322a1474362ac97614900ae.
Model weights: /home/juc049/projects/djev-amd/model. Adapter: /home/juc049/projects/djev-amd/upstream/structured_server.py. Docker network: djev-amd_default.

Model command preserves BF16, served identity dgemma, max length4096, max8 sequences, memory utilization0.35, eager execution, TRITON_ATTN, canvas64, max-logprobs128, prefix caching. Structured API preserves tokenizer/model/canvas64 and its existing decoder implementation. Each representative probe uses one sample, seed0, one step, independent choice.

Reproduce on AMD from /home/juc049/projects/mario-amd/harness:

```sh
python3 serving/start_parallel_djev.py
```

The script never modifies existing containers. It verifies model discovery, API health, and an actual structured choice; full returned evidence is stored in reports/stages/parallel-service-verification.json. All three new endpoints now pass these checks. A premature first launch on18517 reached the adapter before its model was ready; those eight zero-decision infrastructure errors are retained, and gameplay was retried after the structured probe passed.

## Pooling the final stage's candidate trials

After the other stages cleared, the runner gained an optional `--djev-urls` pool.
It assigns whole trials round-robin within a batch, records the selected endpoint
in each reservation and CLI command, and permits at most one active trial per
listed endpoint. This preserves one central stage manifest and its reservation
cap. The existing single `--djev-url` behavior remains unchanged.

```sh
.venv/bin/python scripts/run_reflection_batch.py --world 8 --stage 4 \
  --root runs/stages/8-4/batches --frames 2 --workers 4 \
  --djev-urls http://127.0.0.1:18515 http://127.0.0.1:18516 \
              http://127.0.0.1:18517 http://127.0.0.1:18518 \
  --profiles prompts/reflection/CANDIDATE_A.json prompts/reflection/CANDIDATE_B.json
```

This is trial routing across four independent replicas, not tensor parallelism.
Separate replicas may reduce inference-batch interactions, but that explanation
for earlier trajectory variation remains a hypothesis. A fake-game subprocess
test verifies assignment, non-overlap, manifest accounting and legacy fallback;
the full suite passed65 tests after this addition.
