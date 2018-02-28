import os
from builtins import round as rnd

from game.models import Round, RoundComposition

from utils import utils

import game.room.state


__path__ = os.path.relpath(__file__)


def client_has_to_wait_over_player(u, rm):
    """
    Check if player state is more advanced than the room state.
    The room state is changed only if both players reached this state.
    """

    return (rm.state == game.room.state.tutorial and u.state == game.room.state.pve) or \
        (rm.state == game.room.state.pve and u.state == game.room.state.pvp)


def get_opponent_progression(u, opp):
    """
    :return: The percentage of opponent progression
     in the previous round
    """

    if u.state == game.room.state.pve:
        progression = u.tutorial_progression
    else:
        comp = RoundComposition.objects.filter(player_id=opp.id)
        rd = None

        for c in comp:
            rd = Round.objects.get(round_id=c.round_id)
            if rd.state == game.room.state.pve:
                break

        progression = (rd.t / rd.ending_t) * 100

    return str(rnd(progression))


def go_to_next_round(u, opp, rm):

    utils.log("Going to next round: game.room.state = {}".format(rm.room_state), f=utils.fname(), path=__path__)

    if rm.room_state == game.room.state.tutorial and u.state == game.room.state.tutorial:
        _tutorial_is_done(u=u, opp=opp, rm=rm)

    elif rm.room_state == game.room.state.pve and u.state == game.room.state.pve:
        _pve_is_done(u=u, opp=opp, rm=rm)

    elif rm.room_state == game.room.state.pvp and u.state == game.room.state.pvp:
        _pvp_is_done(u=u, opp=opp, rm=rm)

    else:
        return False

    return True


def _tutorial_is_done(u, opp, rm):

    # change player.state
    u.state = game.room.state.pve
    u.save()

    # if other player has done tutorial, set rm.state to pve
    if rm.trial or opp.state == game.room.state.pve:
        rm.state = game.room.state.pve
        rm.save()


def _pve_is_done(u, opp, rm):

    # load objects
    next_round = Round.objects.get(id=u.room_id, state=game.room.state.pvp)

    # player is assigned to next round id
    u.round_id = next_round.round_id
    u.state = game.room.state.pvp
    u.save()

    # set room state
    if opp.state == game.room.state.pvp:

        rm.state = game.room.state.pvp
        rm.save()


def _pvp_is_done(u, opp, rm):

    # Modify sate of player
    u.state = game.room.state.end
    u.save()

    if opp.state == game.room.state.end:

        # Close room and set state
        rm.opened = False
        rm.save()

        rm.state = game.room.state.end
        rm.save()
