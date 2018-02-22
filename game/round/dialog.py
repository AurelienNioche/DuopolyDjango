import os

from utils import utils

from . import management, state, composition, data

__path__ = os.path.relpath(__file__)


# -------------- Relative to management ------------------------- #

def create_rounds(room_id, ending_t, trial, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    management.create_rounds(room_id=room_id, ending_t=ending_t, trial=trial)


def delete_rounds(room_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    management.delete_rounds(room_id=room_id)


def close_round(round_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    management.close_round(round_id=round_id)


# -------------- Relative to composition ------------------------- #

def include_players_into_round_compositions(room_id, player_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    return composition.include_players_into_round_compositions(room_id, player_id)


# -------------- Relative to state ------------------------- #

# def go_to_next_round(player_id, called_from):
#
#     utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
#     state.go_to_next_round(player_id=player_id)


# def set_time_last_request(player_id, function_name):
#     state.set_time_last_request(player_id, function_name)

def advance_of_one_time_step(round_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    state.advance_of_one_time_step(round_id)


# ----------------- Relative to data ---------------------- #

def register_firm_choices(round_id, agent_id, t, price, position, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    data.register_firm_choices(
        round_id=round_id,
        agent_id=agent_id,
        t=t,
        price=price,
        position=position
    )


def get_positions_and_prices(round_id, t):
    return data.get_positions_and_prices(round_id=round_id, t=t)


def compute_scores(round_id, t, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.function_name(), path=__path__)
    compute_scores(round_id=round_id, t=t)
