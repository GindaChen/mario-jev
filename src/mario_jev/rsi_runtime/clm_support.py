"""Shared JSON helpers and native-frame environment from the frozen CLM run."""

import json

CODEX_BIN = "/home/juc049/.codex/packages/standalone/releases/0.157.1-x86_64-unknown-linux-musl/bin"


def compact(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def atomic(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(compact(value) + "\n")
    tmp.replace(path)


class FixedFrameFactory:
    @staticmethod
    def make(world=1, stage=1):
        if (
            type(world) is not int
            or type(stage) is not int
            or not 1 <= world <= 8
            or not 1 <= stage <= 4
        ):
            raise ValueError("Invalid fixed world/stage")
        from gym_super_mario_bros.smb_env import SuperMarioBrosEnv

        class FixedFrameEnv(SuperMarioBrosEnv):
            def _did_step(self, done):
                pass  # disable upstream frame skipping and post-step RAM writes

        return FixedFrameEnv(target=(world, stage), render_mode="rgb_array")
