"""Native Laya policy with auditable, level-independent observations and prompts."""

import hashlib
import json
from pathlib import Path

import httpx2

from .policy import ACTIONS


def describe(state):
    m = state["mario"]
    parts = [
        f"Mario is {m['motion']}. On ground: {m['grounded']}. Jump button already held: {state['jump_already_held']}.",
        f"Horizontal speed {m.get('vx_px_per_frame')} pixels/frame; vertical speed {m.get('vy_px_per_frame')} (positive means down).",
        f"Blocked moving forward: {state['blocked_forward']}.",
    ]
    objects = [
        o
        for o in state["nearby_objects"]
        if o["kind"] != "flagpole" and not o.get("defeated") and o["dx"] >= -16
    ]
    parts.append(
        "Visible enemies: "
        + (
            ", ".join(
                f"{o['kind']} {o['dx']}px horizontally from Mario, {o['dy']}px vertically (positive below), contact in {o.get('estimated_contact_in_frames')} frames"
                for o in objects[:3]
            )
            or "none"
        )
        + "."
    )
    t = state["terrain"]["summary"]
    parts.append("Obstacle ahead: " + json.dumps(t["nearest_obstacle"]) + ".")
    parts.append(
        "Missing floor ahead: " + json.dumps(t["nearest_empty_column_below_feet"]) + "."
    )
    corridor = state["jump_corridor"]
    parts.append(
        f"Low ceiling before nearest enemy: {corridor['low_ceiling_before_nearest_threat']}; upward headroom there: {corridor['minimum_headroom_before_threat_px']}px."
    )
    parts.append(
        "Landing surfaces relative to Mario: "
        + json.dumps(state["landing_surfaces"]["surfaces"])
        + "."
    )
    parts.append(
        "Floor gaps relative to Mario: "
        + json.dumps(state["landing_surfaces"]["floor_gaps"])
        + "."
    )
    return "\n".join(parts)


class LayaPolicy:
    def __init__(self, base_url, profile):
        self.profile = json.loads(Path(profile).read_text())
        self.digest = hashlib.sha256(Path(profile).read_bytes()).hexdigest()
        self.client = httpx2.Client(base_url=base_url, timeout=60)

    def choose(self, state):
        observation = {"short": describe_short, "scene": describe_scene}.get(
            self.profile.get("observation"), describe
        )(state)
        payload = {"state": observation, "questions": self.profile["questions"]}
        response = self.client.post("/decide", json=payload)
        if not response.is_success:
            raise RuntimeError(f"Laya {response.status_code}: {response.text[:2000]}")
        result = response.json()
        answers = result["answers"]
        movement = answers["movement"]["choice"]
        jump = answers["jump"]["choice"] == "press"
        buttons = {
            "run_right": ["right", "B"],
            "walk_right": ["right"],
            "brake_left": ["left"],
            "dodge_left": ["left"],
            "wait": [],
        }[movement]
        # Mechanical rearming only; the model decides when to request a jump.
        rearm = state["mario"]["grounded"] and state["jump_already_held"]
        if jump and not rearm:
            buttons.append("A")
        action = next(name for name, keys in ACTIONS.items() if keys == buttons)
        return action, {
            "model": result["checkpoint"],
            "profile": self.profile["name"],
            "profile_sha256": self.digest,
            "backend_diagnostics": {"request": payload, "response": result},
            "decisions": {
                "movement": movement,
                "jump": answers["jump"]["choice"],
                "rearm_release": rearm,
            },
        }

    def close(self):
        self.client.close()


def describe_short(state):
    m = state["mario"]
    parts = [
        f"Mario is {m['motion']}. Jump button is {'held' if state['jump_already_held'] else 'released'}.",
        f"Speed to the right: {m.get('vx_px_per_frame')} pixels per frame.",
    ]
    enemies = [
        o
        for o in state["nearby_objects"]
        if o["kind"] != "flagpole" and not o.get("defeated") and o["dx"] >= 0
    ]
    if enemies:
        o = min(enemies, key=lambda o: o["dx"])
        parts.append(
            f"A live {o['kind']} is {o['dx']} pixels to the right and {o['dy']} pixels below Mario. Contact in {o.get('estimated_contact_in_frames')} frames."
        )
    else:
        parts.append("No enemy ahead.")
    t = state["terrain"]["summary"]
    o = t["nearest_obstacle"]
    g = t["nearest_empty_column_below_feet"]
    parts.append(
        f"A solid obstacle is {o['distance_px']} pixels ahead. Its top is {o['height_above_feet_px']} pixels above Mario's feet."
        if o
        else "No solid obstacle ahead."
    )
    parts.append(
        f"The ground ends {g['edge_distance_px']} pixels ahead."
        if g
        else "There is floor ahead."
    )
    gaps = state["landing_surfaces"]["floor_gaps"]
    if gaps:
        parts.append("Visible gaps: " + json.dumps(gaps))
    room = t.get("overhead_clearance_px")
    parts.append(
        f"Overhead clearance is {room} pixels."
        if room is not None
        else "No ceiling immediately above."
    )
    if state["blocked_forward"]:
        parts.append("Mario is pushing against a wall without moving forward.")
    return "\n".join(parts)


def describe_scene(state):
    m = state["mario"]
    t = state["terrain"]["summary"]
    parts = [
        f"Mario is {'standing on the ground' if m['grounded'] else 'airborne and ' + m['motion']}. The jump button is {'held down' if state['jump_already_held'] else 'released'}."
    ]
    hazards = []
    enemies = [
        o
        for o in state["nearby_objects"]
        if o["kind"] != "flagpole" and not o.get("defeated") and o["dx"] >= 0
    ]
    if enemies:
        o = min(enemies, key=lambda o: o["dx"])
        hazards.append(
            f"A dangerous enemy is {o['dx']} pixels ahead, {o['dy']} pixels below Mario; touching its side kills Mario."
        )
    o = t["nearest_obstacle"]
    if o:
        hazards.append(
            f"A solid wall blocks the path {o['distance_px']} pixels ahead. The wall top is {o['height_above_feet_px']} pixels above Mario's feet."
        )
    g = t["nearest_empty_column_below_feet"]
    if g:
        hazards.append(
            f"A hole in the ground starts {g['edge_distance_px']} pixels ahead. Falling into the hole kills Mario."
        )
    parts.extend(hazards or ["Mario is on a clear, flat stretch of terrain."])
    room = t.get("overhead_clearance_px")
    if room is not None:
        parts.append(f"Bricks overhead leave only {room} pixels of upward headroom.")
    corridor = state["jump_corridor"]
    if corridor["low_ceiling_before_nearest_threat"]:
        parts.append(
            f"A low ceiling before the enemy allows only {corridor['minimum_headroom_before_threat_px']} pixels of upward movement."
        )
    if state["blocked_forward"]:
        parts.append("Mario is blocked against the wall.")
    return "\n".join(parts)


class ModularLayaPolicy(LayaPolicy):
    """All tactical case selections are Laya outputs; no distance/action tests."""

    def query(self, state_text, questions, calls):
        payload = {"state": state_text, "questions": questions}
        response = self.client.post("/decide", json=payload)
        if not response.is_success:
            raise RuntimeError(f"Laya {response.status_code}: {response.text[:2000]}")
        result = response.json()
        calls.append({"request": payload, "response": result})
        return result["answers"]

    def choose(self, state):
        calls = []
        q = self.profile["questions"]
        m = state["mario"]
        t = state["terrain"]["summary"]
        movement_state = describe_scene(state)
        if self.profile.get("movement_observation") == "goal_direction":
            movement_state = (
                "Mario's destination is to the right. He needs forward momentum to cross gaps. "
                "A separate controller question decides when to jump over hazards. "
                f"Mario is {m['motion']}."
            )
        movement = self.query(movement_state, {"movement": q["movement"]}, calls)[
            "movement"
        ]["choice"]
        votes = {}
        if m["grounded"]:
            # Identify observed geometry, without deciding whether it warrants an action.
            enemy = state["nearest_threat"]
            wall = t["nearest_obstacle"]
            pit = t["nearest_empty_column_below_feet"]
            background = f"Mario is on the ground, running right at {m.get('vx_px_per_frame') or 0} pixels/frame. The jump button is {'held' if state['jump_already_held'] else 'released'}. "
            observations = {
                "enemy": background
                + (
                    f"An enemy is {enemy['dx']} pixels ahead on the same ground level."
                    if enemy
                    else "There is no enemy ahead."
                ),
                "wall": background
                + (
                    f"A wall is {wall['distance_px']} pixels ahead and {wall['height_above_feet_px']} pixels high."
                    if wall
                    else "There is no wall ahead."
                ),
                "pit": background
                + (
                    f"A pit begins {pit['edge_distance_px']} pixels ahead."
                    if pit
                    else "There is no pit ahead."
                ),
            }
            if self.profile.get("units") in ("body_lengths", "body_lengths_v2"):
                words = [
                    "zero",
                    "one",
                    "two",
                    "three",
                    "four",
                    "five",
                    "six",
                    "seven",
                    "eight",
                    "nine",
                    "ten",
                    "eleven",
                    "twelve",
                    "thirteen",
                    "fourteen",
                    "fifteen",
                    "sixteen",
                    "seventeen",
                    "eighteen",
                    "nineteen",
                    "twenty",
                ]
                distances = {
                    "enemy": enemy["dx"] if enemy else None,
                    "wall": wall["distance_px"] if wall else None,
                    "pit": pit["edge_distance_px"] if pit else None,
                }
                for hazard, distance in distances.items():
                    if distance is None:
                        observations[hazard] = (
                            f"Mario is standing on the ground. There is no {hazard} ahead."
                        )
                    else:
                        body_lengths = max(1, round(distance / 16))
                        amount = (
                            words[body_lengths]
                            if body_lengths < len(words)
                            else str(body_lengths)
                        )
                        observations[hazard] = (
                            f"Mario is standing on the ground. A {hazard} is {amount} body lengths ahead."
                        )
                        if self.profile.get("units") == "body_lengths_v2":
                            article = "An" if hazard == "enemy" else "A"
                            measure = (
                                "within one body length"
                                if distance <= 16
                                else f"about {amount} body {'length' if body_lengths == 1 else 'lengths'}"
                            )
                            observations[hazard] = (
                                f"Mario is standing on the ground. {article} {hazard} is {measure} ahead."
                            )

            low = state["jump_corridor"]["low_ceiling_before_nearest_threat"]
            for hazard, text in observations.items():
                key = "enemy_low" if hazard == "enemy" and low else hazard
                votes[hazard] = self.query(text, {"decision": q[key]}, calls)[
                    "decision"
                ]["choice"]
            jump = any(value == "C" for value in votes.values())
        else:
            text = f"Mario is airborne and {m['motion']}. The jump button is {'held' if state['jump_already_held'] else 'released'}."
            votes["air"] = self.query(text, {"decision": q["air"]}, calls)["decision"][
                "choice"
            ]
            jump = votes["air"] == "A"
        buttons = {
            "run_right": ["right", "B"],
            "walk_right": ["right"],
            "brake_left": ["left"],
            "dodge_left": ["left"],
            "wait": [],
        }[movement]
        rearm = m["grounded"] and state["jump_already_held"]
        if jump and not rearm:
            buttons.append("A")
        action = next(name for name, keys in ACTIONS.items() if keys == buttons)
        return action, {
            "model": calls[0]["response"]["checkpoint"],
            "profile": self.profile["name"],
            "profile_sha256": self.digest,
            "decisions": {
                "movement": movement,
                "votes": votes,
                "jump": jump,
                "rearm_release": rearm,
            },
            "backend_diagnostics": calls,
        }
