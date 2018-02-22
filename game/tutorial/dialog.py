import os

from . import management
from utils import utils

__path__ = os.path.relpath(__file__)


def get_tutorial_progression(player_id, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return management.get_tutorial_progression(player_id=player_id)
