import os

from utils import utils

from . import management, state, composition, data

__path__ = os.path.relpath(__file__)


# -------------- Relative to management ------------------------- #

def create_rounds(room_id, ending_t, trial, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    management.create_rounds(room_id=room_id, ending_t=ending_t, trial=trial)


def delete_rounds(room_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    management.delete_rounds(room_id=room_id)


def close_round(rd, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    management.close_round(rd=rd)


# -------------- Relative to composition ------------------------- #

def include_players_into_round_compositions(room_id, player_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return composition.include_players_into_round_compositions(room_id, player_id)


# ----------------- Relative to data ---------------------- #

def register_firm_choices(rd, agent, t, price, position, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    data.register_firm_choices(
        rd=rd,
        agent=agent,
        t=t,
        price=price,
        position=position
    )


def get_positions_and_prices(round_id, t, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return data.get_positions_and_prices(round_id=round_id, t=t)


def compute_scores(round_id, t, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    compute_scores(round_id=round_id, t=t)
