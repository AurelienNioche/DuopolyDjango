from utils import utils
import os

from . import management

__path__ = os.path.relpath(__file__)


# def go_to_next_round(u, called_from):
#
#     utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
#     management.go_to_next_round(u=u)


def get_opponent_progression(p, opp, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return management.get_opponent_progression(p=p, opp=opp)


def client_has_to_wait_over_player(u, rm, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return management.client_has_to_wait_over_player(u=u, rm=rm)


def player_is_banned(u, rm, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return management.player_is_banned(u=u, rm=rm)
