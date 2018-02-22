from utils import utils

from . import management


def go_to_next_round(player_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    management.go_to_next_round(player_id=player_id)
