"""Native hosted Jev choices using the auditable modular controller."""

import hashlib
import json
from pathlib import Path

from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient

from .laya import ModularLayaPolicy


class ModularJevPolicy(ModularLayaPolicy):
    def __init__(self, model, profile, *, client=None):
        self.previous_movement = None
        self.movement_origin_feet_y = None
        self.current_state = None
        self.profile = json.loads(Path(profile).read_text())
        self.digest = hashlib.sha256(Path(profile).read_bytes()).hexdigest()
        self.client = client or TypeSafeClient(
            model=model,
            timeout=30,
            retry=RetryPolicy(max_retries=self.profile.get("api_retries", 0)),
        )

    def choose(self, state):
        self.current_state = state
        action, info = super().choose(state)
        movement = info["decisions"]["movement"]
        if movement != self.previous_movement:
            self.movement_origin_feet_y = state["mario"]["feet_y"]
        self.previous_movement = movement
        return action, info

    def query(self, state_text, questions, calls):
        if self.profile.get("route_geometry"):
            s = self.current_state
            t = s["terrain"]["summary"]
            if "movement" in questions:
                state_text = {
                    "goal": "Move toward the right exit",
                    "motion": s["mario"]["motion"],
                    "blocked_forward": s["blocked_forward"],
                    "wall": t["nearest_obstacle"],
                    "ceiling_clearance_px": t["overhead_clearance_px"],
                    "feet_y": s["mario"]["feet_y"],
                    "platforms": s["landing_surfaces"]["surfaces"],
                    "previous_movement": self.previous_movement,
                    "movement_origin_feet_y": self.movement_origin_feet_y,
                }
                if self.profile.get("route_displacement"):
                    state_text["vertical_drop_since_direction_change_px"] = (
                        s["mario"]["feet_y"] - self.movement_origin_feet_y
                        if self.movement_origin_feet_y is not None
                        else 0
                    )
                if self.profile.get("route_minimal"):
                    wall = t["nearest_obstacle"]
                    state_text = {
                        "blocked": s["blocked_forward"],
                        "wall_height": wall["height_above_feet_px"] if wall else None,
                        "headroom": t["overhead_clearance_px"],
                        "retreating": self.previous_movement == "brake_left",
                        "drop_px": s["mario"]["feet_y"] - self.movement_origin_feet_y
                        if self.movement_origin_feet_y is not None
                        else 0,
                    }
                if self.profile.get("route_wall_distance"):
                    wall = t["nearest_obstacle"]
                    state_text["wall_distance_px"] = wall["distance_px"] if wall else None
                if self.profile.get("movement_enemies"):
                    enemies = [
                        o
                        for o in s["nearby_objects"]
                        if o["kind"] != "flagpole"
                        and not o.get("defeated")
                        and o["dx"] >= 0
                    ]
                    enemy = min(enemies, key=lambda o: o["dx"]) if enemies else None
                    state_text["enemy_dx"] = enemy["dx"] if enemy else None
                    state_text["enemy_dy"] = enemy["dy"] if enemy else None
                    if self.profile.get("enemy_landing"):
                        state_text["enemy_kind"] = enemy["kind"] if enemy else None
                        state_text["motion"] = s["mario"]["motion"]
                if self.profile.get("route_floor"):
                    floors = s["landing_surfaces"]["surfaces"]
                    state_text["grounded"] = s["mario"]["grounded"]
                    state_text["lowest_floor_drop_px"] = (
                        max(o["top_y"] for o in floors) - s["mario"]["feet_y"]
                        if floors
                        else None
                    )
            elif "wall" in state_text:
                state_text += " Wall geometry: " + json.dumps(
                    {
                        "wall": t["nearest_obstacle"],
                        "ceiling_clearance_px": t["overhead_clearance_px"],
                        "previous_movement": self.previous_movement,
                    }
                )
        if (
            self.profile.get("enemy_vertical")
            and isinstance(state_text, str)
            and "enemy" in state_text
        ):
            enemy = self.current_state["nearest_threat"]
            if enemy:
                state_text += f" Enemy vertical offset is {enemy['dy']} pixels; negative means above Mario, positive means below Mario."
        if self.profile.get("hazard_pixels") and isinstance(state_text, str):
            s = self.current_state
            terrain = s["terrain"]["summary"]
            if "enemy" in state_text:
                enemy = s["nearest_threat"]
                state_text = {
                    "distance_px": enemy["dx"] if enemy else None,
                    "vertical_offset_px": enemy["dy"] if enemy else None,
                }
            elif "wall" in state_text:
                wall = terrain["nearest_obstacle"]
                state_text = {
                    "distance_px": wall["distance_px"] if wall else None,
                    "height_px": wall["height_above_feet_px"] if wall else None,
                    "headroom_px": terrain["overhead_clearance_px"],
                }
            elif "pit" in state_text:
                pit = terrain["nearest_empty_column_below_feet"]
                state_text = {
                    "distance_px": pit["edge_distance_px"] if pit else None,
                    "floor_gaps": s["landing_surfaces"]["floor_gaps"],
                }
        if (
            "movement" in questions
            and self.profile.get("retreat_question")
            and self.previous_movement == "brake_left"
        ):
            s = self.current_state
            floors = s["landing_surfaces"]["surfaces"]
            floor_drop = (
                max(o["top_y"] for o in floors) - s["mario"]["feet_y"]
                if floors
                else None
            )
            state_text = f"Mario is retreating left and is {s['mario']['motion']}. The lowest visible floor is {floor_drop} pixels below his feet. Grounded: {s['mario']['grounded']}."
            if self.profile.get("retreat_drop_fact"):
                drop = (
                    s["mario"]["feet_y"] - self.movement_origin_feet_y
                    if self.movement_origin_feet_y is not None
                    else 0
                )
                state_text += (
                    f" Mario has dropped {drop} pixels since this retreat began."
                )
            questions = {"movement": self.profile["retreat_question"]}
        if self.profile.get("overhead_enemies") and not (
            "movement" in questions and self.previous_movement == "brake_left"
        ):
            s = self.current_state
            above = [
                o
                for o in s["nearby_objects"]
                if o["kind"] != "flagpole"
                and not o.get("defeated")
                and o["dx"] >= 0
                and o["dy"] < 0
            ]
            nearest_above = min(above, key=lambda o: o["dx"]) if above else None
            if isinstance(state_text, str):
                state_text = {"motion": s["mario"]["motion"]}
            state_text["above_enemy_dx"] = (
                nearest_above["dx"] if nearest_above else None
            )
        native = {
            k: Choice(instructions=q["instructions"], criteria=q["criteria"])
            for k, q in questions.items()
        }
        result = self.client.system_one(state=state_text, questions=native)
        answers = {
            k: {
                "choice": a.choice,
                "probabilities": dict(a.probabilities),
                "confidence": a.confidence,
            }
            for k, a in result.answers.items()
        }
        calls.append(
            {
                "request": {"state": state_text, "questions": questions},
                "response": {
                    "checkpoint": result.model,
                    "answers": answers,
                    "usage": {
                        "input_tokens": result.usage.input_tokens,
                        "output_tokens": result.usage.output_tokens,
                    },
                },
            }
        )
        return answers
