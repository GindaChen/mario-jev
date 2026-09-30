"""Fixed-program ablation: remove global memory; never invoke System 2."""

import argparse
import json
import re
import signal
from pathlib import Path

from mario_jev.rsi_runtime.clm_pilot import ClmPilot, digest, validate_program
from mario_jev.rsi_runtime.clm_support import atomic, compact


class FixedNoMemoryPilot(ClmPilot):
    def __init__(self, args):
        if args.resume_from is not None:
            raise ValueError("A fixed ablation starts fresh")
        source = validate_program(json.loads(args.source_program.read_text()))
        self.source_program = source
        self.fixed_program = validate_program({**source, "memory": ""})
        super().__init__(args)
        atomic(self.root / "frozen/source-program.json", source)
        self.manifest.update(
            protocol="clm-fixed-no-memory-v1",
            s2_model=None,
            s2_reasoning=None,
            s2_timeout_s=0,
            reflection_enabled=False,
            fixed_program=True,
            source_program_sha256=digest(compact(source).encode()),
            ablation="Remove only the global memory field and its derived note timer. "
            "Keep source instructions, all candidate descriptions, observations, "
            "controller, checkpoint, seed and model unchanged.",
            experiment_memory="empty on every request; no retrieval or updates",
        )
        atomic(self.root / "manifest.json", self.manifest)
        self.event("fixed_program_frozen", program_sha256=self.program_hash)

    def publish(self):
        # Base initialization calls this once. Further publication is a violation.
        if self.version != 0 or (self.root / "programs/v0000").exists():
            raise RuntimeError("The fixed ablation cannot revise its program")
        self.program = self.fixed_program
        super().publish()

    def reflect_checked(self, summary, rows):
        self.status.update(status="between_attempts", s2_state="disabled")
        self.event("reflection_disabled_prompt_retained", outcome=summary["outcome"])

    def reflect(self, *args, **kwargs):
        raise RuntimeError("System 2 is disabled in the fixed ablation")

    def codex(self, *args, **kwargs):
        raise RuntimeError("No agent process may run in the fixed ablation")

    def attempt_run(self):
        assert self.program == self.fixed_program
        summary, rows = super().attempt_run()
        for row in rows:
            question = row["request"]["questions"]["action"]
            assert question["instructions"] == self.fixed_program["instructions"] + "\n"
            assert question["criteria"] == self.fixed_program["criteria"]
            assert row["request"]["state"]["note_elapsed_frames"] == {}
            assert row["program_version"] == 0
        return summary, rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--control", type=Path, required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--source-program", type=Path, required=True)
    p.add_argument("--endpoint", default="http://127.0.0.1:18432")
    p.add_argument("--max-attempts", type=int, default=3)
    p.add_argument("--wall-limit", type=int, default=600)
    args = p.parse_args()
    args.resume_from = None
    if (
        not re.fullmatch(r"[a-zA-Z0-9_-]{1,45}", args.name)
        or not 1 <= args.max_attempts <= 10
    ):
        p.error("Invalid run name or attempt count")
    pilot = FixedNoMemoryPilot(args)
    signal.signal(signal.SIGTERM, lambda *_: pilot.stop.set())
    signal.signal(signal.SIGINT, lambda *_: pilot.stop.set())
    try:
        pilot.run()
    finally:
        print(compact(pilot.snapshot()), flush=True)


if __name__ == "__main__":
    main()
