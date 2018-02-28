import os

import utils.utils as utils

from game import player

__path__ = os.path.relpath(__file__)


def room_available(rooms, players):

    exclude_missing_players_entries = rooms.exclude(missing_players=0)
    entries = exclude_missing_players_entries.exclude(opened=0)

    for e in entries:
        p_room = players.filter(room_id=e.room_id)
        if p_room:
            for p in p_room:
                if player.dialog.player_is_banned(player_id=p.player_id, called_from=utils.fname()):
                    # management.close(room_id=e.room_id)
                    entry = rooms.get(room_id=e.room_id)
                    entry.opened = 0
                    entry.save()

    entries = rooms.exclude(opened=0)

    utils.log("There are {} available rooms".format(len(entries)), f=utils.fname(), path=__path__)

    room_avail = int(len(entries) > 0)
    return room_avail

#
# def missing_players(player_id):
#
#     p = Players.objects.get(player_id=player_id)
#     rm = Room.objects.get(room_id=p.room_id)
#     n_missing_players = rm.missing_players
#
#     return n_missing_players

