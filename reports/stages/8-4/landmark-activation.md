# Observed-landmark lesson activation

Introduced after r36, to avoid anchoring a maneuver timer to the first sighting of a geographic region when fresh arrivals differ in motion state.

Optional profile note `activate_when` supports `grounded`, `x_min/x_max`, `feet_y_min/feet_y_max`, signed `horizontal_speed_min/max` measured from `vx_px_per_frame`, and `after_note_frames: {note_id: minimum}`. All specified conditions must hold at the same observation. Missing measurements or dependency timers prevent activation. The first qualifying observation starts the note timer at zero and latches activation for that policy instance (the campaign creates a new process for each single fresh episode). Normal note geography, room restrictions and sticky-on-left behavior still govern retrieval afterward.

This adds state-dependent instruction retrieval, not an action override. DJev receives the activated instruction and still chooses among the offered actions. No predicates mean the earlier retrieval behavior. Per-attempt source snapshots identify which runs used this feature.

Validation: 64 tests passed, including new tests for missing observations/dependencies, delayed timer start, latch behavior after takeoff, room/geographic exclusion and model-selected actions. Ruff passed. Source deployed atomically on AMD for subsequent attempts; already-running processes retain their imported version.
