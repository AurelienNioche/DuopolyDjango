import os

from utils import utils

from . import field_of_view, management, info, state

__path__ = os.path.relpath(__file__)


# ------------------- Relative to field of view ------------------- #

def compute_field_of_view(rm, to_send, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    return field_of_view.compute(rm, to_send=to_send)


# ----------------- Relative to management ------------------------- #

def close(rm, called_from):

    utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
    management.close(rm=rm)


# -------------- Relative to state ------------------------------------ #

# def get_state(rm, called_from):
#     utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
#     return state.get(rm=rm)
#
#
# def update_state(rm, room_state, called_from):
#     utils.log("Called by '{}'".format(called_from), f=utils.fname(), path=__path__)
#     state.update(rm, state=room_state)
