import os
import secrets

import utils.utils as utils

from game.models import Round

from . import data, composition, state

__path__ = os.path.relpath(__file__)


def create_rounds(room_id, ending_t, trial):

    class Pvp:
        n_real_players = 1 if trial else 2
        name = "pvp"

    class Pve:
        n_real_players = 1
        name = "pve"

    # noinspection PyTypeChecker
    round_types = (Pve, ) * 2 + (Pvp, )

    for rt in round_types:

        # create round and its composition
        round_id = secrets.token_hex(10)

        while Round.objects.filter(round_id=round_id).first():
            round_id = secrets.token_hex(10)

        rd = Round(
            round_id=round_id,
            room_id=room_id,
            real_players=rt.n_real_players,
            missing_players=rt.n_real_players,
            ending_t=ending_t,
            state=rt.name,
            opened=1,
            t=0,
        )

        rd.save()

        composition.create(round_id=round_id, n_real_players=rt.n_real_players)

        data.init(round_id=round_id)
        state.init(round_id=round_id, ending_t=ending_t)


def delete_rounds(room_id):

    entries = Round.objects.filter(room_id=room_id)

    for e in entries:

        composition.delete(round_id=e.round_id)
        state.delete(round_id=e.round_id)
        data.delete(round_id=e.round_id)

        e.delete()


def close_round(round_id):

    entry = Round.objects.get(round_id=round_id)
    entry.opened = 0
    entry.save(force_update=True)

    # Log
    utils.log("The round {} is now closed.".format(round_id), f=utils.function_name(), path=__path__)
