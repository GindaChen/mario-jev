"""Publication-boundary tests; no emulator or model calls."""

import json
import tempfile
import unittest
from pathlib import Path

from build_clm_audit import reflection, safe_text, source_path, tools_from_log, write


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_secret_export_fails_closed(self):
        for value in (
            "Bearer " + "a" * 30,
            "sk-" + "b" * 30,
            '{"refresh_token":"secret"}',
        ):
            with self.assertRaises(ValueError):
                write(self.root / "data.json", {"text": value})
        self.assertFalse((self.root / "data.json").exists())

    def test_only_host_paths_redacted(self):
        value = "read /run/attempts/0001; source /raid/user/private/file.json"
        self.assertEqual(
            safe_text(value), "read /run/attempts/0001; source [host-path]"
        )

    def test_artifact_cannot_escape_root(self):
        with self.assertRaises(ValueError):
            source_path(self.root, "../secret")
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            source_path(self.root, "escape/secret")

    def test_no_reasoning_or_session_metadata(self):
        path = self.root / "log.jsonl"
        events = [
            {"type": "thread.started", "thread_id": "private"},
            {
                "type": "item.completed",
                "item": {"id": "r", "type": "reasoning", "text": "private analysis"},
            },
            {
                "type": "item.completed",
                "item": {"id": "m", "type": "agent_message", "text": "not published"},
            },
            {
                "type": "item.started",
                "item": {
                    "id": "c",
                    "type": "command_execution",
                    "command": "cat /run/a.json",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "c",
                    "type": "command_execution",
                    "command": "cat /run/a.json",
                    "aggregated_output": "actual output",
                    "exit_code": 0,
                    "status": "completed",
                },
            },
        ]
        path.write_text("\n".join(json.dumps(e) for e in events))
        result = tools_from_log(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["aggregated_output"], "actual output")
        self.assertNotIn("private", json.dumps(result))

    def test_rejected_answer_not_presented_as_published(self):
        folder = self.root / "reflections/0001"
        folder.mkdir(parents=True)
        program = {"instructions": "Move safely.", "criteria": {"jump": "another jump"}}
        packet = {
            "summary": {"attempt_id": 1, "program_version": 0},
            "current_program": program,
        }
        answer = {
            "hypothesis": "A fix",
            "program": {
                "instructions": "Move right.",
                "criteria": {"jump": "a new jump"},
            },
        }
        write(folder / "input.json", packet)
        write(folder / "answer.json", answer)
        (folder / "input.txt").write_text("Recorded input")
        r = reflection(
            self.root, folder, {}, [], [{"image_sha256": "a"}, {"image_sha256": "b"}]
        )
        self.assertEqual(r["status"], "rejected")
        self.assertFalse(r["criteria_equal"])
        self.assertIsNone(r["next_outcome"])
        self.assertTrue(r["criteria_diff"])
        self.assertEqual(r["proposal"], answer)


if __name__ == "__main__":
    unittest.main()
