import os

import utils.utils as utils

from game.models import Room, Players

from game import player
from . import management

__path__ = os.path.relpath(__file__)


def room_available():

    exclude_missing_players_entries = Room.objects.exclude(missing_players=0)
    entries = exclude_missing_players_entries.exclude(opened=0)

    for e in entries:
        players = Players.objects.filter(room_id=e.room_id)
        if players:
            for p in players:
                if player.dialog.player_is_banned(player_id=p.player_id, called_from=utils.fname()):
                    management.close(room_id=e.room_id)

    entries = Room.objects.all().exclude(opened=0)

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
