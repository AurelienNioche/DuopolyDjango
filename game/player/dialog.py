from utils import utils
import os

from . import management

__path__ = os.path.relpath(__file__)


def go_to_next_round(p, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    management.go_to_next_round(p=p)


def get_opponent_progression(player_id, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return management.get_opponent_progression(player_id)


def client_has_to_wait_over_player(player_id, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return management.client_has_to_wait_over_player(player_id)


def player_is_banned(player_id, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return management.player_is_banned(player_id)
