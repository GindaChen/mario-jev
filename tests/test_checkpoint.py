import json

from mario_jev.checkpoint import resume_prefix


def test_rewind_uses_executed_frames_and_rounds_back(tmp_path):
    path = tmp_path / "run.jsonl"
    rows = [{"type": "config", "env": "SuperMarioBros-1-1-v0", "episodes": 1}]
    for i, frames in enumerate([4, 2, 4, 4]):
        rows.append(
            {
                "type": "decision",
                "episode": 0,
                "decision": i,
                "action": "right",
                "frames_executed": frames,
                "result": {"terminated": False, "truncated": False},
            }
        )
    path.write_text("\n".join(map(json.dumps, rows)))
    _, prefix = resume_prefix(path, 5)
    assert [r["frames_executed"] for r in prefix] == [4, 2]
    assert resume_prefix(path, 300)[1] == []
