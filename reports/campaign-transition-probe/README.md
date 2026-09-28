# Full-game transition diagnostics

These are deterministic diagnostic replays, not fresh model games or evidence of a completed continuous campaign. No model requests were made. The probes do not directly write ROM/RAM. The final-castle probe loads a native initial 8-4 snapshot into the full-game environment, as explicitly authorized for this diagnostic.

## Confirmed 1-1 to 1-2 transition

`probe.py` replays the existing 1-1 winning trace in `SuperMarioBros-v0`. Every action agrees with the stage trace until the final transition; 1,392 external environment steps are executed.

The final step (decision 361) returns old-stage event info: world 1, stage 1, x=3161, `flag_get=true`, `terminated=false`. Before that same call returns, the wrapper advances its internal cutscene and the actual RAM/screen become world 1, stage 2, area 3, x=40, player_state=8, time=400. No extra no-input cutscene step is required. The probe executes one redundant NOP afterward only to confirm that the next stage is already controllable.

This mismatch follows the installed `NESEnv.step` order: advance frame; calculate reward/termination/info; call `_did_step`; return the current screen with the previously captured info. `_did_step` can advance many hidden frames. Read returned info for the event that just occurred; read post-step RAM or `_get_info()` for the state to route next. Do not merge them without preserving which snapshot each field describes.

The same issue occurs at internal pipes. In the unguarded final-castle diagnostic, the first reported post-state comparison difference is decision 307: old returned x=280 versus new post-transition x=1848. That is a snapshot-timing mismatch, not action replay divergence. The guarded probe compares returned x plus post RAM y, matching the legacy trace convention, and finds no divergences.

## Death and life handling

After entering 1-2, holding right without jumping causes natural deaths. Each fatal step returns `is_dying=true` and the previous life count, while post-step RAM is already at the respawn point x=40 with the life count decremented. The observed sequence is 2 → 1 → 0, representing three playable lives.

On the final death, the returned event still has `terminated=false`, but post-step RAM has life=255, `is_game_over=true`, and player_state=6. The next external step reports `terminated=true`. A runner should recognize the post-step game-over state immediately instead of issuing another model action.

Break a multi-frame action as soon as returned death/clear info or a post-step stage/life change is seen. Otherwise remaining frames can operate the new stage or consume the next life using an action chosen for the previous state. Reset controller history, local timers, and stage progress on transition/retry. An ordinary full-environment `reset()` starts the backed-up initial game state, not an arbitrary later stage.

## Final 8-4 victory: confirmed hang and guard

`probe_final.py` loads a native initial 8-4 snapshot into `SuperMarioBros-v0` and replays the existing 8-4 winner. At decision 1261, external step 2507, the final axe makes the wrapper enter victory-cutscene handling. That environment call does not return normally. A diagnostic counter aborts it after 10,000 hidden `_frame_advance` calls. The remaining state is world 8, stage 4, x=4964, life=2, time=272, `flag_get=true`, `is_world_over=true`, `is_game_over=false`.

`probe_final_guarded.py` adds only this diagnostic Python hook before the original `_did_step`:

```python
if env._world == 8 and env._stage == 4 and env._flag_get:
    return
original_did_step(done)
```

With that hook, every recorded action matches the legacy winner coordinates. The final step returns immediately at x=4805 with `flag_get=true`, `is_world_over=true`, `terminated=false`, and zero hidden cutscene frames. Thus breaking after `env.step()` returns is insufficient without guarding the handler itself. Campaign completion must be recognized explicitly from the final-stage clear event; vanilla full-game termination only tests game over, not victory.

## Additional source-level pitfalls

Full-environment reward accounting retains `_x_position_max` and `_completion_rewarded` across stages. Do not use those fields as stage-local progress or assume every flag grants a new completion reward. Maintain separate campaign/stage accounting.

The installed wrapper already contains timer shortcuts and death-animation RAM operations in `_did_step`. These probes introduce no new direct RAM edits; this distinction matters when documenting emulator behavior.

Local and AMD source files were hash-verified identical:

- `gym_super_mario_bros.smb_env`: `7beed0a62068e04473d57c2ca62235b0b361879128174c2a5225118b9bed8bbf`
- `nes_py.nes_env`: `f4c19152ceff11c98ab5fa8e3ae9e972960cb6570379b4e63549d4e6b5141ca6`

## Evidence

- `result.json`: real full-game 1-1 transition and three natural deaths.
- `final-result.json`: bounded unguarded final-castle hang.
- `final-guarded-result.json`: successful diagnostic guard, no replay divergence.
- Corresponding Python scripts and stdout files reproduce the probes without any API calls.

## AMD confirmation

The normal 1-1 transition/death probe and the guarded 8-4 probe were also executed on AMD. Their complete JSON results are byte-identical to the local results (SHA-256 checks passed). The first AMD 1-1 invocation found its winning trace absent from `deliverables/stages/1-1`; the existing local immutable trace was copied there and the probe rerun successfully. The unguarded bounded-hang probe was executed locally; installed wrapper source hashes match AMD.
