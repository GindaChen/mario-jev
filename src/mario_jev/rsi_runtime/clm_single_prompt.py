"""One immutable prompt per attempt; failure reflection rewrites only that prompt."""

import argparse
import json
import re
import signal
from pathlib import Path

from mario_jev.reflection import DEFAULT_CRITERIA
from mario_jev.rsi_runtime.clm_pilot import ClmPilot, digest, validate_program
from mario_jev.rsi_runtime.clm_support import atomic, compact


def validate_single_program(program, fixed_criteria):
    if not isinstance(program, dict) or set(program) != {"instructions", "criteria"}:
        raise ValueError(
            "Single-prompt programs have only instructions and frozen criteria; no memory"
        )
    instructions = program["instructions"]
    if (
        not isinstance(instructions, str)
        or not instructions.strip()
        or len(instructions) > 6000
    ):
        raise ValueError("Instructions must contain 1 to 6000 characters")
    if (
        set(fixed_criteria) != set(DEFAULT_CRITERIA)
        or program["criteria"] != fixed_criteria
    ):
        raise ValueError("All eight candidate descriptions are frozen")
    return json.loads(compact(program))


def single_profile(program, version):
    return {
        "name": f"clm-single-prompt-v{version}",
        "mode": "reflection",
        "one_frame_rearm": True,
        "single_prompt": True,
        "instructions": program["instructions"],
        "criteria": program["criteria"],
    }


class SinglePromptPilot(ClmPilot):
    def __init__(self, args):
        if args.resume_from is not None:
            raise ValueError(
                "Single-prompt runs start fresh; continuation needs an explicit audit"
            )
        self.source_program = validate_program(
            json.loads(args.source_program.read_text())
        )
        self.fixed_criteria = self.source_program["criteria"]
        self.reflection_enabled = not args.fixed
        super().__init__(args)
        atomic(self.root / "frozen/source-program.json", self.source_program)
        self.manifest.update(
            protocol="clm-single-prompt-v1",
            reflection_enabled=self.reflection_enabled,
            fixed_program=not self.reflection_enabled,
            initial_memory=None,
            editable_fields=["instructions"] if self.reflection_enabled else [],
            source_program_sha256=digest(compact(self.source_program).encode()),
            experiment_memory="No note objects, retrieval, per-note timers or separate memory field. "
            "Previous global note text is retained in initial instructions.",
            initial_prompt_recipe="source.instructions + newline + source.memory, exact bytes",
            candidate_descriptions="Frozen from source program for the entire experiment",
            note_elapsed_frames="Absent from every actual model request",
        )
        if not self.reflection_enabled:
            self.manifest.update(s2_model=None, s2_reasoning=None, s2_timeout_s=0)
        atomic(self.root / "manifest.json", self.manifest)
        self.event(
            "single_prompt_initialized",
            reflection_enabled=self.reflection_enabled,
            program_sha256=self.program_hash,
        )

    def initial_program(self, template):
        source = self.source_program
        return self.validate_candidate(
            {
                "instructions": source["instructions"] + "\n" + source["memory"],
                "criteria": self.fixed_criteria,
            }
        )

    def build_profile(self):
        return single_profile(self.validate_candidate(self.program), self.version)

    def validate_candidate(self, candidate):
        return validate_single_program(candidate, self.fixed_criteria)

    def editable_description(self):
        return (
            "Only the single instructions string may change. All candidate descriptions are frozen. "
            "There are no memory notes, retrieval, note timers, or within-attempt prompt updates. "
            "Any useful reflection lesson must be integrated into that single prompt."
        )

    def publish(self):
        if not self.reflection_enabled and (self.root / "programs/v0000").exists():
            raise RuntimeError("The fixed baseline cannot publish a revision")
        super().publish()

    def reflect_checked(self, summary, rows):
        if self.reflection_enabled:
            return super().reflect_checked(summary, rows)
        self.status.update(status="between_attempts", s2_state="disabled")
        self.event("reflection_disabled_prompt_retained", outcome=summary["outcome"])

    def codex(self, *args, **kwargs):
        if not self.reflection_enabled:
            raise RuntimeError("No agent process may run in the fixed baseline")
        return super().codex(*args, **kwargs)

    def attempt_run(self):
        expected = compact(self.program)
        summary, rows = super().attempt_run()
        assert compact(self.program) == expected
        for row in rows:
            question = row["request"]["questions"]["action"]
            assert question["instructions"] == self.program["instructions"]
            assert question["criteria"] == self.fixed_criteria
            assert "note_elapsed_frames" not in row["request"]["state"]
            assert row["program_version"] == self.version
        return summary, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--source-program", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:18432")
    parser.add_argument("--max-attempts", type=int, default=50)
    parser.add_argument("--wall-limit", type=int, default=3600)
    parser.add_argument("--fixed", action="store_true")
    args = parser.parse_args()
    args.resume_from = None
    if (
        not re.fullmatch(r"[a-zA-Z0-9_-]{1,45}", args.name)
        or not 1 <= args.max_attempts <= 50
        or args.wall_limit <= 0
    ):
        parser.error("Invalid run name, attempt count or wall limit")
    pilot = SinglePromptPilot(args)
    signal.signal(signal.SIGTERM, lambda *_: pilot.stop.set())
    signal.signal(signal.SIGINT, lambda *_: pilot.stop.set())
    try:
        pilot.run()
    finally:
        print(compact(pilot.snapshot()), flush=True)


if __name__ == "__main__":
    main()
