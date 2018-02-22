import os

from utils import utils

from . import field_of_view, management, info, state

__path__ = os.path.relpath(__file__)


# ------------------- Relative to field of view ------------------- #

def compute_field_of_view(room_id, to_send, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return field_of_view.compute(room_id=room_id, to_send=to_send)


# ----------------- Relative to management ------------------------- #

def close(room_id, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    management.close(room_id=room_id)


def is_trial(player_id, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return info.is_trial(player_id)


# -------------- Relative to state ------------------------------------ #

def get_state(room_id, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return state.get(room_id)


def update_state(room_id, room_state, called_from):
    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    state.update(room_id=room_id, state=room_state)
