"""Situation-based instructions with a fixed action menu and relative observations."""

import hashlib
import json
from pathlib import Path

from typesafe_sdk import Choice

from .djev import DjevPolicy
from .policy import ACTIONS

CRITERIA = {
    "wait": "Release all buttons.",
    "right": "Hold right.",
    "right_jump": "Hold right and jump.",
    "right_run": "Hold right and run.",
    "right_run_jump": "Hold right, run and jump.",
    "left": "Hold left to brake or move left.",
    "left_jump": "Hold left and jump.",
    "jump": "Hold jump without horizontal input.",
    "down": "Hold down.",
}


def observation(state):
    """Whitelist measured geometry; exclude absolute coordinates and room IDs."""
    mario = state["mario"]
    terrain = state["terrain"]["summary"]
    wall = terrain.get("nearest_obstacle")
    pit = terrain.get("nearest_empty_column_below_feet")
    return {
        "mario": {
            k: mario.get(k)
            for k in (
                "grounded",
                "motion",
                "vx_px_per_frame",
                "vy_px_per_frame",
                "status",
            )
        },
        "action_frames": state["action_frames"],
        "jump_held": state["jump_already_held"],
        "headroom_px": terrain.get("overhead_clearance_px"),
        "wall": None
        if wall is None
        else {k: wall.get(k) for k in ("distance_px", "height_above_feet_px")},
        "missing_floor": None
        if pit is None
        else {"edge_distance_px": pit.get("edge_distance_px")},
        "landing_surfaces": [
            {
                k: s.get(k)
                for k in ("start_dx", "end_dx", "height_above_current_feet_px")
            }
            for s in state.get("landing_surfaces", {}).get("surfaces", [])
        ],
        "floor_gaps": [
            {
                k: g.get(k)
                for k in ("start_dx", "end_dx", "observed_width_px", "far_edge_visible")
            }
            for g in state.get("landing_surfaces", {}).get("floor_gaps", [])
        ],
        "enemies": [
            {k: e.get(k) for k in ("kind", "dx", "dy")}
            for e in state.get("nearby_objects", [])
            if not e.get("defeated") and e["kind"] != "flagpole"
        ],
        "blocked_forward": bool(state.get("blocked_forward")),
    }


class SituationalDjevPolicy(DjevPolicy):
    def __init__(self, base_url, profile, **kwargs):
        data = Path(profile).read_bytes()
        config = json.loads(data)
        allowed = {
            "name",
            "mode",
            "stage",
            "instructions",
            "stage_guidance",
            "one_frame_rearm",
            "extra_solid_tiles",
        }
        if set(config) - allowed or config.get("mode") != "situational":
            raise ValueError(
                "Situational profiles cannot configure routing, criteria or coordinate triggers"
            )
        for key in ("name", "instructions"):
            if not isinstance(config.get(key), str) or not config[key]:
                raise ValueError(f"Missing text field: {key}")
        if config.get("extra_solid_tiles", []) not in ([], [22, 23, 24]):
            raise ValueError(
                "Only the measured 1-3 platform tile extension is supported"
            )
        super().__init__(base_url, **kwargs)
        self.profile = config
        self.profile_digest = hashlib.sha256(data).hexdigest()

    def choose(self, state):
        measured = observation(state)
        if "stage" in self.profile:
            measured["stage"] = self.profile["stage"]
        question = {
            "instructions": self.profile["instructions"]
            + (
                "\nStage guidance: " + self.profile["stage_guidance"]
                if "stage_guidance" in self.profile
                else ""
            ),
            "criteria": dict(CRITERIA),
        }
        result = self.client.system_one(
            state=measured, questions={"action": Choice(**question)}
        )
        answer = result.answers["action"]
        selected = answer.choice
        if selected not in CRITERIA:
            raise ValueError("Model selected an unsupported action")
        rearm = bool(
            state["mario"]["grounded"]
            and state["jump_already_held"]
            and "A" in ACTIONS[selected]
        )
        buttons = [b for b in ACTIONS[selected] if not (rearm and b == "A")]
        executed = next(k for k, v in ACTIONS.items() if v == buttons)
        return executed, {
            "backend": "djev",
            "model": result.model,
            "profile": self.profile["name"],
            "profile_sha256": self.profile_digest,
            "decisions": {
                "selected_action": selected,
                "executed_action": executed,
                "rearm_release": rearm,
            },
            "requested_action_frames": 1
            if rearm and self.profile.get("one_frame_rearm")
            else state["action_frames"],
            "backend_diagnostics": [
                {
                    "request": {"state": measured, "questions": {"action": question}},
                    "response": {
                        "choice": selected,
                        "confidence": answer.confidence,
                        "probabilities": dict(answer.probabilities),
                        "usage": {
                            "input_tokens": result.usage.input_tokens,
                            "output_tokens": result.usage.output_tokens,
                        },
                        "backend_diagnostics": (self.transport.last_response or {}).get(
                            "diagnostics", {}
                        ),
                    },
                }
            ],
        }
