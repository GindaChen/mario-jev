"""DJev chooses live buttons using retrieved, offline-authored reflection notes."""

from typesafe_sdk import Choice

from .djev import ModularDjevPolicy
from .policy import ACTIONS

DEFAULT_CRITERIA = {
    "right_run": "Run right with jump released.",
    "right_run_jump": "Run right and press or hold jump.",
    "right": "Move right without run or jump.",
    "right_jump": "Move right and press or hold jump without run.",
    "left": "Brake or retreat left with jump released.",
    "left_jump": "Move left and press or hold jump.",
    "wait": "Release all buttons.",
    "jump": "Press or hold jump without horizontal input.",
}


class ReflectionDjevPolicy(ModularDjevPolicy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_action = None
        self.last_grounded_support_feet_y = None
        self.retreat_origin_support_feet_y = None
        self.previous_state = None
        self.sticky_notes = []
        self.reflection_engaged = False
        self.elapsed_frames = 0
        self.note_entry_frames = {}

    def _activation_matches(self, note, state):
        """Gate instruction retrieval on measured landmarks, never select actions."""
        trigger = note.get("activate_when", {})
        bounds = {
            "x": "x",
            "feet_y": "feet_y",
            "horizontal_speed": "vx_px_per_frame",
        }
        supported = {"grounded", "after_note_frames"} | {
            f"{name}_{side}" for name in bounds for side in ("min", "max")
        }
        if set(trigger) - supported:
            raise ValueError("Unsupported reflection activation predicate")
        mario = state["mario"]
        if "grounded" in trigger and mario.get("grounded") != trigger["grounded"]:
            return False
        for name, field in bounds.items():
            value = mario.get(field)
            for side in ("min", "max"):
                key = f"{name}_{side}"
                if key in trigger and (
                    value is None
                    or (side == "min" and value < trigger[key])
                    or (side == "max" and value > trigger[key])
                ):
                    return False
        for dependency, minimum in trigger.get("after_note_frames", {}).items():
            if dependency not in self.note_entry_frames or (
                self.elapsed_frames - self.note_entry_frames[dependency] < minimum
            ):
                return False
        return True

    def choose(self, state):
        mario = state["mario"]
        self.reflection_engaged |= mario["x"] >= self.profile.get(
            "reflection_start_x", float("-inf")
        )
        if not self.reflection_engaged:
            return super().choose(state)
        if mario["grounded"]:
            self.last_grounded_support_feet_y = mario["feet_y"]
        self.elapsed_frames += (
            state.get("physics", {}).get("motion_estimate_interval_frames") or 0
        )
        candidates = [
            note
            for note in self.profile.get("memory_notes", [])
            if note.get("min_x", float("-inf"))
            <= mario["x"]
            <= note.get("max_x", float("inf"))
            and (
                "room_ids" not in note
                or state.get("room", {}).get("area_data_address") in note["room_ids"]
            )
        ]
        notes = []
        for note in candidates:
            key = note.get("id", note["instructions"])
            if key in self.note_entry_frames or self._activation_matches(note, state):
                notes.append(note)
                self.note_entry_frames.setdefault(key, self.elapsed_frames)
        if self.last_action in ("left", "left_jump"):
            for note in self.sticky_notes:
                if note not in notes and (
                    "room_ids" not in note
                    or state.get("room", {}).get("area_data_address") in note["room_ids"]
                ):
                    notes.append(note)
        self.sticky_notes = [note for note in notes if note.get("sticky_on_left")]
        for note in notes:
            self.note_entry_frames.setdefault(
                note.get("id", note["instructions"]), self.elapsed_frames
            )
        note_elapsed = {
            note.get("id", note["instructions"]): self.elapsed_frames
            - self.note_entry_frames[note.get("id", note["instructions"])]
            for note in notes
        }
        criteria = dict(self.profile.get("criteria", DEFAULT_CRITERIA))
        for note in notes:
            if "criteria" in note:
                criteria = dict(note["criteria"])
        if not criteria or any(action not in ACTIONS for action in criteria):
            raise ValueError(
                "Reflection criteria must name supported controller actions"
            )
        instructions = self.profile.get(
            "instructions",
            self.profile.get("global_instructions", "Choose Mario's next action."),
        )
        # Local questions can explicitly replace a conflicting global question.
        # This changes prompt text only; the model still selects every action.
        if any(note.get("replace_instructions") for note in notes):
            for note in notes:
                if note.get("replace_instructions"):
                    instructions = note["instructions"]
                else:
                    instructions += "\n" + note["instructions"]
        else:
            instructions += "\n" + "\n".join(note["instructions"] for note in notes)
        terrain = state["terrain"]["summary"]
        enemies = []
        previous = self.previous_state
        old_objects = (
            {obj["slot"]: obj for obj in previous["nearby_objects"]} if previous else {}
        )
        elapsed = state.get("physics", {}).get("motion_estimate_interval_frames")
        for obj in state["nearby_objects"]:
            if obj["kind"] == "flagpole" or obj.get("defeated"):
                continue
            enemy = dict(obj)
            old = old_objects.get(obj["slot"])
            if old and old["kind"] == obj["kind"] and elapsed:
                vy = (
                    mario["y"] + obj["dy"] - previous["mario"]["y"] - old["dy"]
                ) / elapsed
                enemy["vy_px_per_frame"] = round(vy, 3) if abs(vy) <= 8 else None
            enemies.append(enemy)
        observation = {
            "mario": {
                key: mario.get(key)
                for key in (
                    "x",
                    "feet_y",
                    "grounded",
                    "motion",
                    "vx_px_per_frame",
                    "vy_px_per_frame",
                    "status",
                )
            },
            "headroom_px": terrain.get("overhead_clearance_px"),
            "wall": terrain.get("nearest_obstacle"),
            "pit": terrain.get("nearest_empty_column_below_feet"),
            "landing_surfaces": state.get("landing_surfaces", {}),
            "enemies": enemies,
            "blocked_forward": state.get("blocked_forward"),
            "jump_held": state["jump_already_held"],
            "last_action": self.last_action,
            "last_grounded_support_feet_y": self.last_grounded_support_feet_y,
            "retreat_origin_support_feet_y": self.retreat_origin_support_feet_y,
            "drop_from_retreat_origin_px": (
                mario["feet_y"] - self.retreat_origin_support_feet_y
                if self.retreat_origin_support_feet_y is not None
                else None
            ),
        }
        if self.profile.get("compact_state"):
            observation["enemies"] = [
                {k: e.get(k) for k in ("kind", "dx", "dy", "vy_px_per_frame")}
                for e in sorted(enemies, key=lambda e: e["dx"])
                if -12 <= e["dx"] <= 160
            ][:4]
            observation["landing_surfaces"] = {
                "floor_gaps": state.get("landing_surfaces", {}).get("floor_gaps", [])
            }
        if self.profile.get("observation_style") == "facts":
            wall = terrain.get("nearest_obstacle")
            room = terrain.get("overhead_clearance_px")
            thresholds = dict(self.profile.get("thresholds", {}))
            for note in notes:
                thresholds.update(note.get("thresholds", {}))
            ahead = [e for e in enemies if e["dx"] >= 0]
            near = min(ahead, key=lambda e: e["dx"]) if ahead else None
            gap = state.get("landing_surfaces", {}).get("floor_gaps", [])
            pit = terrain.get("nearest_empty_column_below_feet")
            observation = {
                "x": mario["x"],
                "feet_y": mario["feet_y"],
                "grounded": mario["grounded"],
                "motion": mario["motion"],
                "horizontal_speed": mario.get("vx_px_per_frame"),
                "jump_held": state["jump_already_held"],
                "enemy_ahead": None
                if near is None
                else {k: near.get(k) for k in ("kind", "dx", "dy")},
                "enemy_within_jump_distance": near is not None
                and 0 <= near["dx"] <= thresholds.get("enemy", 40)
                and near["dy"] >= -8,
                "enemy_above_within_48px": any(
                    0 <= e["dx"] <= 48 and e["dy"] < -8 for e in ahead
                ),
                "enemy_above_within_braking_distance": any(
                    0 <= e["dx"] <= thresholds.get("above", 64) and e["dy"] < -8
                    for e in ahead
                ),
                "jump_elapsed_frames": (state.get("current_jump") or {}).get(
                    "elapsed_frames", 0
                ),
                "wall_within_40px": wall is not None and wall["distance_px"] <= 40,
                "wall_fits_headroom": wall is not None
                and (room is None or wall["height_above_feet_px"] <= room),
                "headroom_px": room,
                "floor_gap_within_takeoff_distance": bool(gap)
                and pit is not None
                and pit["edge_distance_px"] <= thresholds.get("pit", 24),
                "last_action": self.last_action,
                "retreat_origin_support_feet_y": self.retreat_origin_support_feet_y,
            }
        # Optional measured height facts for a retrieved maneuver. No action override.
        for note in notes:
            if "clearance_feet_y" in note:
                observation["above_maneuver_clearance"] = (
                    mario["feet_y"] < note["clearance_feet_y"]
                    or (
                        "wrapped_above_feet_y" in note
                        and mario["feet_y"] > note["wrapped_above_feet_y"]
                    )
                )
        if self.profile.get("include_room_metadata") and "room" in state:
            observation["room"] = state["room"]
        observation["note_elapsed_frames"] = note_elapsed
        for note in notes:
            if "observation_fields" in note:
                observation = {
                    key: observation[key]
                    for key in note["observation_fields"]
                    if key in observation
                }
        routing_records = []
        route_choice = None
        router = next(
            (note["instruction_router"] for note in reversed(notes)
             if "instruction_router" in note), None
        )
        if router:
            routes = router["routes"]
            route_state = {
                key: observation[key] for key in router["state_fields"]
                if key in observation
            }
            route_question = {
                "instructions": router["instructions"],
                "criteria": {key: value["description"] for key, value in routes.items()},
            }
            routed = self.client.system_one(
                state=route_state, questions={"instruction_set": Choice(**route_question)}
            )
            route_answer = routed.answers["instruction_set"]
            route_choice = route_answer.choice
            if route_choice not in routes:
                raise ValueError("DJev selected an unknown instruction set")
            instructions = routes[route_choice]["instructions"]
            criteria = dict(routes[route_choice]["criteria"])
            if "action_state_fields" in routes[route_choice]:
                observation = {
                    key: observation[key]
                    for key in routes[route_choice]["action_state_fields"]
                    if key in observation
                }
            if not criteria or any(action not in ACTIONS for action in criteria):
                raise ValueError("Routed criteria must name supported controller actions")
            routing_records.append({
                "purpose": "instruction_selection",
                "request": {"state": route_state, "questions": {"instruction_set": route_question}},
                "response": {
                    "model": routed.model, "choice": route_choice,
                    "confidence": route_answer.confidence,
                    "probabilities": dict(route_answer.probabilities),
                    "usage": {"input_tokens": routed.usage.input_tokens,
                              "output_tokens": routed.usage.output_tokens},
                },
            })
        question = {"instructions": instructions, "criteria": criteria}
        result = self.client.system_one(
            state=observation, questions={"action": Choice(**question)}
        )
        answer = result.answers["action"]
        selected = answer.choice
        if selected not in criteria:
            raise ValueError("DJev selected an action outside the offered criteria")
        rearm = bool(
            mario["grounded"]
            and state["jump_already_held"]
            and "A" in ACTIONS[selected]
        )
        buttons = [
            button for button in ACTIONS[selected] if not (rearm and button == "A")
        ]
        action = next(name for name, keys in ACTIONS.items() if keys == buttons)
        if action in ("left", "left_jump"):
            if self.last_action not in ("left", "left_jump"):
                self.retreat_origin_support_feet_y = self.last_grounded_support_feet_y
        else:
            self.retreat_origin_support_feet_y = None
        self.last_action = action
        self.previous_state = state
        response = {
            "checkpoint": result.model,
            "answers": {
                "action": {
                    "choice": selected,
                    "confidence": answer.confidence,
                    "probabilities": dict(answer.probabilities),
                }
            },
            "usage": {
                "input_tokens": result.usage.input_tokens,
                "output_tokens": result.usage.output_tokens,
            },
            "backend_diagnostics": (self.transport.last_response or {}).get(
                "diagnostics", {}
            ),
        }
        return action, {
            "model": result.model,
            "backend": "djev",
            "profile": self.profile["name"],
            "profile_sha256": self.digest,
            "active_memory_notes": notes,
            "decisions": {"selected_action": selected, "rearm_release": rearm,
                          **({"instruction_set": route_choice} if router else {})},
            "requested_action_frames": 1
            if rearm and self.profile.get("one_frame_rearm")
            else state["action_frames"],
            "backend_diagnostics": routing_records + [
                {
                    "request": {
                        "state": observation,
                        "questions": {"action": question},
                        "inference": {
                            "samples": 1,
                            "seed": 0,
                            **self.profile.get("inference", {}),
                        },
                    },
                    "response": response,
                }
            ],
        }
