import os
import secrets

import utils.utils as utils

from game.models import Round

from . import data, composition, state

__path__ = os.path.relpath(__file__)


# def create_rounds(room_id, ending_t, trial):
#
#     class Pvp:
#         real_players = 1 if trial else 2
#         name = "pvp"
#
#     class Pve:
#         real_players = 1
#         name = "pve"
#
#     # noinspection PyTypeChecker
#     round_types = (Pve, ) * 2 + (Pvp, )
#
#     for rt in round_types:
#
#         # create round and its composition
#         round_id = secrets.token_hex(10)
#
#         while Round.objects.filter(round_id=round_id).first():
#             round_id = secrets.token_hex(10)
#
#         rd = Round(
#             round_id=round_id,
#             room_id=room_id,
#             real_players=rt.real_players,
#             missing_players=rt.real_players,
#             ending_t=ending_t,
#             state=rt.name,
#             t=0,
#         )
#
#         rd.save()
#
#         composition.create(rd=rd, n_real_players=rt.n_real_players)
#
#         data.init(rd=rd)
#         state.init(rd=rd, ending_t=ending_t)

#
# def delete_rounds(room_id):
#
#     entries = Round.objects.filter(room_id=room_id)
#
#     for rd in entries:
#
#         composition.delete(rd=rd)
#         state.delete(rd=rd)
#         data.delete(rd=rd)
#
#         rd.delete()


# def close_round(rd):
#
#     rd.opened = 0
#     rd.save()
#
#     # Log
#     utils.log("The round {} is now closed.".format(rd), f=utils.fname(), path=__path__)