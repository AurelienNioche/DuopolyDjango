import os

import utils.utils as utils

from game.models import Room, Players

__path__ = os.path.relpath(__file__)


def room_available():

    exclude_missing_players_entries = Room.objects.exclude(missing_players=0)
    entries = exclude_missing_players_entries.exclude(opened=0)
    utils.log("There are {} available rooms".format(len(entries)), f=utils.fname(), path=__path__)

    return int(len(entries) > 0)


def missing_players(player_id):

    p = Players.objects.get(player_id=player_id)
    rm = Room.objects.get(room_id=p.room_id)
    n_missing_players = rm.missing_players

    return n_missing_players


def is_trial(player_id):

    p = Players.objects.get(player_id=player_id)
    rm = Room.objects.get(room_id=p.room_id)

    return rm.trial
