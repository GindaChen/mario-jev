import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "campaign", Path(__file__).parents[1] / "scripts/run_campaign.py"
)
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


class BoundaryEnv:
    def __init__(self, death=False):
        self.unwrapped = self
        self.death = death
        self.steps = 0
        self.ram = {0x6D: 0, 0x86: 40, 0xCE: 176, 0x1D: 0}

    def _get_info(self):
        return {
            "world": 1,
            "stage": 1 if not self.steps or self.death else 2,
            "life": 2 if not self.steps else 1 if self.death else 2,
            "x_pos": 40,
            "is_game_over": False,
        }

    def step(self, action):
        self.steps += 1
        return (
            None,
            0,
            False,
            False,
            {
                "world": 1,
                "stage": 1,
                "life": 2,
                "flag_get": not self.death,
                "is_dying": self.death,
                "x_pos": 3161,
            },
        )


def test_breaks_at_natural_transition_and_returns_post_cutscene_info():
    env = BoundaryEnv()
    info, raw, _, _, _, samples = campaign.execute_campaign_action(env, "right_run", 4)
    assert env.steps == 1 and len(samples) == 1
    assert raw["flag_get"] and raw["stage"] == 1
    assert info["stage"] == 2


def test_breaks_at_death_even_when_environment_has_already_respawned():
    env = BoundaryEnv(death=True)
    info, raw, _, terminated, _, _ = campaign.execute_campaign_action(
        env, "right_run", 4
    )
    assert env.steps == 1 and not terminated
    assert raw["is_dying"] and info["life"] == 1


def test_final_cutscene_guard_only_skips_already_won_final_stage():
    class Game:
        _world, _stage, _flag_get = 8, 4, True

        def __init__(self):
            self.unwrapped = self
            self.calls = []

        def _did_step(self, done):
            self.calls.append(done)

    game = Game()
    campaign.guard_final_cutscene(game)
    game._did_step(False)
    assert game.calls == []
    game._flag_get = False
    game._did_step(False)
    assert game.calls == [False]
    game._flag_get = True
    game._world = 7
    game._did_step(False)
    assert game.calls == [False, False]
