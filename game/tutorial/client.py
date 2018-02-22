import os

import utils.utils as utils

from game.models import Players

from game import round

__path__ = os.path.relpath(__file__)


def tutorial_done(player_id):

    round.dialog.go_to_next_round(
        player_id=player_id,
        called_from=__path__ + ":" + utils.function_name()
    )


def record_tutorial_progression(player_id, tutorial_progression):

    p = Players.objects.get(player_id=player_id)
    p.tutorial_progression = tutorial_progression * 100
    p.save(force_update=True)
