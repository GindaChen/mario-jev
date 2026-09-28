"""Native full-game stepping: no gameplay RAM writes or hidden frame skips."""

from gym_super_mario_bros.smb_env import SuperMarioBrosEnv
from nes_py.wrappers import JoypadSpace

from mario_jev.policy import ACTIONS

STAGES = [f"{world}-{stage}" for world in range(1, 9) for stage in range(1, 5)]


class NativeFullGameEnv(SuperMarioBrosEnv):
    """Boot via controller input; preserve every subsequent ROM frame."""

    def _skip_start_screen(self):
        # Called once by upstream __init__, immediately before its reset backup.
        # Unlike the upstream implementation, do not zero pre-level timers or
        # wait until the clock has already ticked below its initial value.
        self.boot_actions = []
        for frame in range(3600):
            action = 8 if self._read_mem(0x0770) == 0 and frame % 2 == 0 else 0
            self._frame_advance(action)
            self.boot_actions.append(action)
            if (
                self._read_mem(0x0770) == 1
                and self._player_state == 8
                and self._time > 0
            ):
                self._did_reset()
                return
        raise RuntimeError("Native controller-only startup did not reach 1-1")

    def _did_step(self, done):
        # Upstream skips cutscenes, accelerates death and rewrites area timers.
        # A native step must remain exactly one NES frame, even after the axe.
        pass


def make_full_game(seed=123):
    env = JoypadSpace(
        NativeFullGameEnv(render_mode="rgb_array"), list(ACTIONS.values())
    )
    _, info = env.reset(seed=seed)
    if stage_of(info) != "1-1":
        env.close()
        raise RuntimeError("Full-game reset must start at 1-1")
    return env, info


def stage_of(info):
    return f"{info['world']}-{info['stage']}"


def playable(info):
    return info["player_state"] == 8 and not info["is_world_over"]


def died(before, after):
    return (
        after["is_dead"]
        or after["is_dying"]
        or after["is_game_over"]
        or after["life"] < before["life"]
    )


class RunProgress:
    """Credit only ordered native transitions within this single attempt."""

    def __init__(self):
        self.stage = "1-1"
        self.cleared = []
        self.finished = False

    def observe(self, before, after):
        if died(before, after):
            return "death"
        # ROM stage/world counters may be intermediate during a transition.
        # Validate their destination only when control returns to the player.
        destination = stage_of(after)
        if playable(after) and destination != self.stage:
            index = STAGES.index(self.stage)
            if index == len(STAGES) - 1 or destination != STAGES[index + 1]:
                return "unexpected_stage_transition"
            self.cleared.append(self.stage)
            self.stage = destination
        # Wait for the game's end-of-world mode, not a transient axe/enemy flag.
        if self.stage == "8-4" and destination == "8-4" and after["is_world_over"]:
            if self.cleared != STAGES[:-1]:
                return "invalid_completion"
            self.cleared.append("8-4")
            self.finished = True
            return "completed"
        return None
