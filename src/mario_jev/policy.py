"""Policies return a controller action and diagnostics."""

import hashlib
import json
from pathlib import Path

from typesafe_sdk import Choice, Noul, RetryPolicy, TypeSafeClient

ACTIONS = {
    "wait": [],
    "right": ["right"],
    "right_jump": ["right", "A"],
    "right_run": ["right", "B"],
    "right_run_jump": ["right", "B", "A"],
    "left": ["left"],
    "left_jump": ["left", "A"],
    "jump": ["A"],
    "down": ["down"],
}


class JevPolicy:
    def __init__(self, model="jev-latest", *, client=None, profile=None):
        self.profile = json.loads(Path(profile).read_text()) if profile else None
        self.previous_decision = None
        self.profile_digest = (
            hashlib.sha256(Path(profile).read_bytes()).hexdigest() if profile else None
        )
        self.client = (
            client
            if client is not None
            else TypeSafeClient(
                model=model, timeout=15, retry=RetryPolicy(max_retries=0)
            )
        )
        self.questions = {
            "movement": Choice(
                instructions="Choose horizontal movement for the next action_frames. Progress right toward the flag. Use recent_frames (four consecutive emulator frame samples) and the before/action/after transition history and current_jump to estimate where Mario will descend. Inspect landing_surfaces: crossing a gap horizontally is insufficient if Mario hits the far bank below its top. On stairs before a gap, prefer landing on a high step and rearming a second jump over launching an early jump from the foot of the stairs that will descend into the far wall. Use walk for tight positioning, brake if overshooting a landing, and wait only if moving is unsafe. Use jump_corridor to anticipate ceilings ahead. Under low bricks, a long early jump can hit the ceiling and land into an enemy. Prefer a controlled approach; brake_left creates space if the enemy is dangerously close and A must be released to rearm. Walking/releasing B does not instantly remove running momentum. Jump is decided separately; do not select wait just because an obstacle requires jumping.",
                criteria={
                    "run_right": "Hold right+B for normal forward progress and long jumps",
                    "walk_right": "Hold right for slower precision",
                    "brake_left": "Hold left to brake/retreat",
                    "wait": "Release horizontal buttons",
                },
            ),
            "start_jump": Noul(
                instructions="Is it time to START a jump now to avoid the nearest enemy, obstacle, or pit? Use recent_decisions before/after motion, last_jump, current_jump, and landing_surfaces to judge takeoff timing and landing height. Treat stairs plus a following pit as a sequence: climb/land on a suitable upper step, release A, then launch across the pit with enough height to land ON the far bank. Do not assume a jump from the bottom of the stairs can clear the whole sequence. Evaluate the upcoming approach using distances, velocity and contact frames. Jump BEFORE collision with about 8-16 frames to gain clearance. If grounded, A released, same-height live enemy 50-70px ahead while running, this is usually a good time to jump. LOW CEILING EXCEPTION: when jump_corridor.low_ceiling_before_nearest_threat is true, ignore the normal early-jump distance rule. An early jump 70-90px from the enemy can bump the bricks and land before reaching it. Approach and time a shorter hop nearer the enemy (roughly 25-45px ahead), or brake to position near a ceiling opening. Still jump before contact; do not treat low ceilings as a blanket reason to never jump. If headroom is below 16px, seek an opening rather than assuming a hop will clear. Do not wait until contact. A grounded Mario blocked against a nearby pipe/wall with overhead clearance is a strong reason to jump now, even at zero measured velocity. A nearest_obstacle within 48px needs a jump to climb over its top. IMPORTANT: nearest_empty_column_below_feet means missing floor. When grounded and its edge_distance_px is within 48px, START a jump before walking off, even if it could be a drop. Falling into a pit is fatal and cannot be rescued by pressing A in midair. False if airborne or A already held, or clear ground with no approaching hazard."
            ),
            "ceiling_hop": Noul(
                instructions="For a SAME-HEIGHT enemy under LOW BRICKS, is NOW the right spacing to launch a SHORT HOP? A ceiling-truncated hop should reach the enemy before landing. On a running approach with about 32px headroom, wait while enemy dx is above 45px (dx=79 is too early), then hop at about 25-45px. Answer false if enemy is still far away, airborne, A already held, or headroom below 16px. Answer true when grounded, A released, enemy roughly 25-45px ahead and enough headroom to lift feet above it. Example: dx79, grounded, headroom32 -> false; dx35, grounded, headroom32 -> true. This question is only used for a low-ceiling enemy approach, not for pipes or pits."
            ),
            "sustain_jump": Noul(
                instructions="Should A remain held to sustain the CURRENT jump? Use current_jump elapsed_frames, distance and height plus the before/after history. Inspect landing_surfaces for the next supported top and its height. While rising toward a raised far bank, preserve height; pressing A after descent begins cannot restore a jump. Landing on a step and jumping again may be necessary for a following pit. True during ascent when more height/distance is needed to clear an enemy, pipe or pit. A nearby obstacle whose top is still above Mario feet needs more height. While rising over missing floor, hold A to maximize jump distance until landing support is ahead. False when grounded, descending, or sufficient clearance is already achieved and a shorter jump helps landing. Check jump_corridor: holding A cannot push through bricks or undo a ceiling collision. Release A after an apparent head bump or during descent so another jump is armed on landing. Preserve enough horizontal progress to cross or stomp the enemy before landing. Holding A cannot start a second midair jump."
            ),
        }

        if self.profile:
            self.questions = {
                k: (Choice(**v) if k == "movement" else Noul(**v))
                for k, v in self.profile["questions"].items()
            }

    def choose(self, state):
        observation = state
        if self.profile and self.profile.get("observation") == "compact":
            observation = {
                k: state[k]
                for k in (
                    "mario",
                    "action_frames",
                    "jump_already_held",
                    "nearest_threat",
                    "blocked_forward",
                    "jump_corridor",
                    "landing_surfaces",
                )
            }
            observation["mario"] = {
                k: v for k, v in state["mario"].items() if k not in ("x", "y")
            }
            observation["terrain"] = state["terrain"]["summary"]
        if self.profile and self.profile.get("observation") == "minimal":
            terrain = state["terrain"]["summary"]
            enemy = state["nearest_threat"]
            wall = terrain["nearest_obstacle"]
            pit = terrain["nearest_empty_column_below_feet"]
            observation = {
                "motion": state["mario"]["motion"],
                "grounded": state["mario"]["grounded"],
                "jump_held": state["jump_already_held"],
                "enemy_distance_px": enemy["dx"] if enemy else None,
                "wall_distance_px": wall["distance_px"] if wall else None,
                "wall_height_px": wall["height_above_feet_px"] if wall else None,
                "ceiling_clearance_px": terrain["overhead_clearance_px"],
                "pit_edge_distance_px": pit["edge_distance_px"] if pit else None,
                "blocked_forward": state["blocked_forward"],
                "feet_y": state["mario"]["feet_y"],
                "floor_gaps": state["landing_surfaces"]["floor_gaps"],
                "platforms": state["landing_surfaces"]["surfaces"],
            }
        if self.profile and self.profile.get("remember_last_decision"):
            observation["previous_decision"] = self.previous_decision
        response = self.client.system_one(state=observation, questions=self.questions)
        movement = response.answers["movement"]
        start = response.answers["start_jump"].noul
        sustain = response.answers["sustain_jump"].noul
        corridor = state.get("jump_corridor", {})
        summary = state.get("terrain", {}).get("summary", {})
        ceiling_approach = bool(
            corridor.get("low_ceiling_before_nearest_threat")
            and not summary.get("nearest_obstacle")
            and not summary.get("nearest_empty_column_below_feet")
        )
        ceiling_hop = response.answers["ceiling_hop"].noul
        if self.profile and self.profile.get("ceiling_routing") == "unified":
            ceiling_approach = False
        if ceiling_approach:
            start = ceiling_hop
        grounded = state["mario"]["grounded"]
        jump = (
            (start >= 0.5 and not state["jump_already_held"])
            if grounded
            else sustain >= 0.5
        )
        buttons = {
            "run_right": ["right", "B"],
            "walk_right": ["right"],
            "brake_left": ["left"],
            "wait": [],
        }[movement.choice]
        if jump:
            buttons = [*buttons, "A"]
        action = next(
            name for name, candidate in ACTIONS.items() if candidate == buttons
        )
        self.previous_decision = {
            "movement": movement.choice,
            "jump_pressed": jump,
            "feet_y": state["mario"].get("feet_y"),
            "blocked_forward": state.get("blocked_forward"),
        }
        return action, {
            "profile": self.profile["name"] if self.profile else "legacy",
            "profile_sha256": self.profile_digest,
            "backend_diagnostics": {
                "state": observation,
                "questions": {
                    k: {
                        "instructions": v.instructions,
                        **({"criteria": v.criteria} if hasattr(v, "criteria") else {}),
                    }
                    for k, v in self.questions.items()
                },
            },
            "confidence": movement.confidence,
            "probabilities": dict(movement.probabilities),
            "decisions": {
                "movement": movement.choice,
                "start_jump": response.answers["start_jump"].noul,
                "ceiling_hop": ceiling_hop,
                "jump_timing_source": "ceiling_hop"
                if ceiling_approach
                else "start_jump",
                "sustain_jump": sustain,
                "jump_pressed": jump,
            },
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }

    def close(self):
        self.client.close()


class ScriptedPolicy:
    """Simple jump-and-run baseline; no claim of optimal play."""

    def choose(self, state):
        mario = state["mario"]
        if not mario["grounded"]:
            return "right_run_jump", {}
        if state["jump_already_held"]:
            return "right_run", {}
        enemy = any(
            0 < obj["dx"] < 64 and abs(obj["dy"]) < 40 and obj["kind"] != "flagpole"
            for obj in state["nearby_objects"]
        )
        obstacle = False
        gap = False
        feet_row = max(0, min(12, (mario["y"] + 32 - 32) // 16))
        for col in state["terrain"]["columns"]:
            if 16 <= col["dx"] <= 48:
                obstacle |= bool(col["tiles"][max(0, feet_row - 1)])
                gap |= not any(col["tiles"][feet_row:])
        return ("right_run_jump" if enemy or obstacle or gap else "right_run"), {}

    def close(self):
        pass
