import copy
import json
from pathlib import Path

import httpx2

from mario_jev.reflection import ReflectionDjevPolicy


def test_reflection_obeys_model_and_preserves_ground_support(tmp_path):
    profile = tmp_path / "profile.json"
    profile.write_text(
        json.dumps(
            {
                "name": "test",
                "mode": "reflection",
                "one_frame_rearm": True,
                "instructions": "Choose buttons.",
                "memory_notes": [
                    {
                        "min_x": 0,
                        "max_x": 99999,
                        "instructions": "Drop below the ledge.",
                    }
                ],
            }
        )
    )
    selected = ["left"]
    calls = []

    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        return httpx2.Response(
            200,
            json={
                "model": "dgemma",
                "answers": {
                    "action": {
                        "type": "choice",
                        "choice": selected[0],
                        "confidence": 1.0,
                        "probabilities": {
                            key: float(key == selected[0])
                            for key in body["questions"]["action"]["criteria"]
                        },
                    }
                },
                "usage": {"input_tokens": 10, "output_tokens": 8},
            },
        )

    policy = ReflectionDjevPolicy(
        "http://localhost:18515",
        profile,
        api_path="/v1/systemone",
        transport=httpx2.MockTransport(handle),
    )
    state = json.loads((Path(__file__).parent / "fixtures/laya_wall.json").read_text())
    state["mario"].update(grounded=True, feet_y=144)
    state["action_frames"] = 4
    state["jump_already_held"] = False
    try:
        action, info = policy.choose(state)
        assert action == "left"  # A wall cannot override the model's no-jump action.
        assert info["active_memory_notes"][0]["instructions"] == "Drop below the ledge."
        second = copy.deepcopy(state)
        second["mario"].update(grounded=False, feet_y=126)
        assert policy.choose(second)[0] == "left"
        assert calls[-1]["state"]["retreat_origin_support_feet_y"] == 144
        assert calls[-1]["state"]["drop_from_retreat_origin_px"] == -18
        selected[0] = "wait"
        assert policy.choose(second)[0] == "wait"
        selected[0] = "right_run_jump"
        state["jump_already_held"] = True
        action, info = policy.choose(state)
        assert action == "right_run"
        assert info["decisions"]["selected_action"] == "right_run_jump"
        assert info["decisions"]["rearm_release"]
        assert info["requested_action_frames"] == 1
    finally:
        policy.close()


def make_policy(tmp_path, choices, **profile_options):
    """Exercise SDK validation/transport while controlling only model outputs."""
    profile = tmp_path / "additional-profile.json"
    profile.write_text(
        json.dumps(
            {
                "name": "test",
                "instructions": "Choose the next action.",
                **profile_options,
            }
        )
    )
    calls = []
    outputs = iter(choices)

    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        choice = next(outputs)
        return httpx2.Response(
            200,
            json={
                "model": "dgemma",
                "answers": {
                    "action": {
                        "type": "choice",
                        "choice": choice,
                        "confidence": 1.0,
                        "probabilities": {
                            key: float(key == choice)
                            for key in body["questions"]["action"]["criteria"]
                        },
                    }
                },
                "usage": {"input_tokens": 10, "output_tokens": 8},
            },
        )

    policy = ReflectionDjevPolicy(
        "http://localhost:18515",
        profile,
        api_path="/v1/systemone",
        transport=httpx2.MockTransport(handle),
    )
    state = json.loads((Path(__file__).parent / "fixtures/laya_wall.json").read_text())
    state["action_frames"] = 4
    state["jump_already_held"] = False
    state["mario"].update(grounded=True, feet_y=144)
    return policy, state, calls


def test_hybrid_remains_engaged_after_retreat(tmp_path, monkeypatch):
    from mario_jev.djev import ModularDjevPolicy

    fallback_states = []

    def fallback(self, state):
        fallback_states.append(state["mario"]["x"])
        return "right_run", {"fallback": True}

    monkeypatch.setattr(ModularDjevPolicy, "choose", fallback)
    policy, state, calls = make_policy(
        tmp_path, ["left", "left"], reflection_start_x=940
    )
    try:
        state["mario"]["x"] = 930
        assert policy.choose(state)[1] == {"fallback": True}
        state["mario"]["x"] = 950
        assert policy.choose(state)[0] == "left"
        state["mario"]["x"] = 920
        assert policy.choose(state)[0] == "left"
        assert fallback_states == [930]
        assert len(calls) == 2
    finally:
        policy.close()


def test_sticky_lesson_survives_boundary_until_model_resumes_right(tmp_path):
    lesson = {
        "id": "ledge",
        "min_x": 940,
        "max_x": 1020,
        "sticky_on_left": True,
        "instructions": "Remember the retreat.",
        "criteria": {"left": "Retreat", "right_run": "Resume"},
    }
    policy, state, calls = make_policy(
        tmp_path,
        ["left", "left", "right_run", "wait"],
        memory_notes=[lesson],
    )
    try:
        state["mario"]["x"] = 950
        assert policy.choose(state)[1]["active_memory_notes"] == [lesson]
        state["mario"]["x"] = 920
        assert policy.choose(state)[1]["active_memory_notes"] == [lesson]
        assert policy.choose(state)[1]["active_memory_notes"] == [lesson]
        action, info = policy.choose(state)
        assert action == "wait"
        assert info["active_memory_notes"] == []
        assert (
            "Remember the retreat."
            not in calls[-1]["questions"]["action"]["instructions"]
        )
        assert "wait" in calls[-1]["questions"]["action"]["criteria"]
    finally:
        policy.close()


def test_facts_leave_action_to_model_and_rearm_only_one_frame(tmp_path):
    policy, state, calls = make_policy(
        tmp_path,
        ["wait", "left", "right_run_jump", "right_run_jump"],
        observation_style="facts",
        one_frame_rearm=True,
    )
    state["nearby_objects"] = [
        {
            "slot": 0,
            "kind": "goomba",
            "dx": 20,
            "dy": 0,
            "defeated": False,
        }
    ]
    try:
        for expected in ["wait", "left"]:
            action, info = policy.choose(state)
            assert action == expected
            assert info["requested_action_frames"] == 4
            facts = calls[-1]["state"]
            assert facts["enemy_within_jump_distance"] is True
            assert (
                not {"action", "chosen_action", "recommended_action", "selected_action"}
                & facts.keys()
            )
        state["jump_already_held"] = True
        action, info = policy.choose(state)
        assert action == "right_run"
        assert info["requested_action_frames"] == 1
        assert info["decisions"]["rearm_release"] is True
        state["jump_already_held"] = False
        action, info = policy.choose(state)
        assert action == "right_run_jump"
        assert info["requested_action_frames"] == 4
        assert info["decisions"]["rearm_release"] is False
    finally:
        policy.close()


def test_optional_maneuver_height_fact_does_not_override_model(tmp_path):
    lesson = {"min_x": 3000, "max_x": 3070, "instructions": "Clear the wall.",
              "clearance_feet_y": 48, "wrapped_above_feet_y": 240}
    policy, state, calls = make_policy(tmp_path, ["wait"] * 4,
                                       observation_style="facts", memory_notes=[lesson])
    try:
        state["mario"].update(x=3012, feet_y=160)
        assert policy.choose(state)[0] == "wait"
        assert calls[-1]["state"]["above_maneuver_clearance"] is False
        state["mario"]["feet_y"] = 37
        assert policy.choose(state)[0] == "wait"
        assert calls[-1]["state"]["above_maneuver_clearance"] is True
        state["mario"]["feet_y"] = 283
        policy.choose(state)
        assert calls[-1]["state"]["above_maneuver_clearance"] is True
        state["mario"]["x"] = 3100
        policy.choose(state)
        assert "above_maneuver_clearance" not in calls[-1]["state"]
    finally:
        policy.close()


def test_local_question_replacement_is_scoped_and_model_keeps_control(tmp_path):
    policy, state, calls = make_policy(
        tmp_path,
        ["wait", "left"],
        instructions="Global motion question.",
        memory_notes=[{
            "min_x": 100, "max_x": 200,
            "replace_instructions": True,
            "instructions": "Local timer question.",
        }],
    )
    try:
        state["mario"]["x"] = 150
        assert policy.choose(state)[0] == "wait"
        assert calls[-1]["questions"]["action"]["instructions"] == "Local timer question."
        state["mario"]["x"] = 250
        assert policy.choose(state)[0] == "left"
        assert calls[-1]["questions"]["action"]["instructions"] == "Global motion question.\n"
    finally:
        policy.close()


def test_explicit_pipe_action_is_model_selected(tmp_path):
    policy, state, calls = make_policy(
        tmp_path, ["down", "wait"],
        criteria={"down": "Enter the pipe.", "wait": "Wait."},
    )
    try:
        assert policy.choose(state)[0] == "down"
        assert policy.choose(state)[0] == "wait"
        assert set(calls[-1]["questions"]["action"]["criteria"]) == {"down", "wait"}
    finally:
        policy.close()


def test_room_scoped_lesson_and_observation(tmp_path):
    policy, state, calls = make_policy(
        tmp_path, ["left", "wait"], include_room_metadata=True,
        memory_notes=[{"room_ids": [1234], "sticky_on_left": True, "instructions": "Enter this room's pipe."}],
    )
    try:
        state["room"] = {"area_data_address": 1234, "area_type": 3}
        assert policy.choose(state)[0] == "left"
        assert "Enter this room's pipe." in calls[-1]["questions"]["action"]["instructions"]
        assert calls[-1]["state"]["room"] == state["room"]
        state["room"] = {"area_data_address": 5678, "area_type": 0}
        assert policy.choose(state)[0] == "wait"
        assert "Enter this room's pipe." not in calls[-1]["questions"]["action"]["instructions"]
    finally:
        policy.close()


def test_landmark_activation_starts_timer_then_latches_without_forcing_action(tmp_path):
    approach = {"id": "approach", "instructions": "Observe the approach."}
    lesson = {
        "id": "recovery", "min_x": 2300, "max_x": 2500,
        "room_ids": [41980],
        "activate_when": {
            "grounded": True, "feet_y_min": 200,
            "horizontal_speed_max": 0, "x_min": 2360, "x_max": 2380,
            "after_note_frames": {"approach": 8},
        },
        "instructions": "Begin the recovered maneuver.",
    }
    policy, state, calls = make_policy(
        tmp_path, ["wait"] * 5 + ["left", "right_run_jump"] + ["wait"] * 3,
        memory_notes=[approach, lesson],
    )
    state["physics"] = {"motion_estimate_interval_frames": 4}
    state["room"] = {"area_data_address": 41980}
    state["mario"].update(x=2370, feet_y=208, grounded=False, vx_px_per_frame=1)
    try:
        # Geography alone must not start the maneuver's clock.
        assert policy.choose(state)[1]["active_memory_notes"] == [approach]
        state["mario"]["grounded"] = True
        assert policy.choose(state)[1]["active_memory_notes"] == [approach]
        state["mario"]["vx_px_per_frame"] = None
        assert policy.choose(state)[1]["active_memory_notes"] == [approach]
        state["mario"].update(vx_px_per_frame=0, feet_y=190)
        assert policy.choose(state)[1]["active_memory_notes"] == [approach]
        state["mario"].update(feet_y=208, x=2390)
        assert policy.choose(state)[1]["active_memory_notes"] == [approach]
        assert "recovery" not in policy.note_entry_frames
        state["mario"]["x"] = 2370
        action, info = policy.choose(state)
        assert action == "left"  # Retrieval does not force a planned jump.
        assert info["active_memory_notes"] == [approach, lesson]
        assert calls[-1]["state"]["note_elapsed_frames"]["recovery"] == 0
        state["mario"].update(x=2400, feet_y=120, grounded=False, vx_px_per_frame=2)
        assert policy.choose(state)[0] == "right_run_jump"
        assert calls[-1]["state"]["note_elapsed_frames"]["recovery"] == 4
        # A latched trigger cannot bypass its room or geographic scope.
        state["room"]["area_data_address"] = 42000
        assert policy.choose(state)[1]["active_memory_notes"] == [approach]
        state["room"]["area_data_address"] = 41980
        state["mario"]["x"] = 2600
        assert policy.choose(state)[1]["active_memory_notes"] == [approach]
        state["mario"]["x"] = 2400
        assert policy.choose(state)[1]["active_memory_notes"] == [approach, lesson]
        assert calls[-1]["state"]["note_elapsed_frames"]["recovery"] == 16
    finally:
        policy.close()


def test_landmark_activation_requires_observed_dependency(tmp_path):
    lesson = {
        "id": "later", "instructions": "Only after an observed earlier lesson.",
        "activate_when": {"after_note_frames": {"absent": 0}},
    }
    policy, state, calls = make_policy(tmp_path, ["wait"], memory_notes=[lesson])
    try:
        assert policy.choose(state)[1]["active_memory_notes"] == []
        assert calls[-1]["state"]["note_elapsed_frames"] == {}
    finally:
        policy.close()


def test_instruction_router_uses_model_choice_and_logs_both_queries(tmp_path):
    profile = tmp_path / 'router.json'
    profile.write_text(json.dumps({
        'name': 'router-test', 'mode': 'reflection', 'observation_style': 'facts',
        'memory_notes': [{'id': 'route', 'instructions': 'Default.',
            'instruction_router': {'instructions': 'Choose the instruction set.',
                'state_fields': ['note_elapsed_frames'],
                'routes': {
                    'cross': {'description': 'Cross the area.', 'instructions': 'Cross now.',
                              'criteria': {'right_run': 'Run.', 'right_run_jump': 'Jump.'}},
                    'enter': {'description': 'Enter the pipe.', 'instructions': 'Align now.', 'action_state_fields': ['x'],
                              'criteria': {'left': 'Left.', 'down': 'Enter.'}}}}}]}))
    calls = []
    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        key = next(iter(body['questions']))
        choice = 'enter' if key == 'instruction_set' else 'left'
        return httpx2.Response(200, json={'model': 'dgemma', 'answers': {
            key: {'type': 'choice', 'choice': choice, 'confidence': 1.0,
                  'probabilities': {k: float(k == choice) for k in body['questions'][key]['criteria']}}},
            'usage': {'input_tokens': 10, 'output_tokens': 8}})
    policy = ReflectionDjevPolicy('http://localhost:18515', profile,
        api_path='/v1/systemone', transport=httpx2.MockTransport(handle))
    state = json.loads((Path(__file__).parent / 'fixtures/laya_wall.json').read_text())
    state['action_frames'] = 4
    state['jump_already_held'] = False
    try:
        action, diagnostics = policy.choose(state)
        assert action == 'left'
        assert len(calls) == 2
        assert calls[0]['state'] == {'note_elapsed_frames': {'route': 0}}
        assert calls[1]['questions']['action']['instructions'] == 'Align now.'
        assert calls[1]['state'] == {'x': state['mario']['x']}
        assert set(calls[1]['questions']['action']['criteria']) == {'left', 'down'}
        assert diagnostics['decisions']['instruction_set'] == 'enter'
        assert diagnostics['backend_diagnostics'][0]['purpose'] == 'instruction_selection'
    finally:
        policy.close()


def test_local_observation_projection_does_not_choose_action(tmp_path):
    policy, state, calls = make_policy(tmp_path, ['left'], observation_style='facts', memory_notes=[{
        'instructions': 'Choose based on grounded.', 'observation_fields': ['grounded'],
        'replace_instructions': True,
        'criteria': {'left': 'Left.', 'right_run_jump': 'Jump.'},
    }])
    try:
        action, _ = policy.choose(state)
        assert calls[0]['state'] == {'grounded': True}
        assert action == 'left'
    finally:
        policy.close()
