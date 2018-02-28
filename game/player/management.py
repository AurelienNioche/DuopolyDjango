import os
from builtins import round as rnd

from game.models import Round, RoundComposition

import game.room.state


__path__ = os.path.relpath(__file__)


def client_has_to_wait_over_player(u, rm):
    """
    Check if player state is more advanced than the room state.
    The room state is changed only if both players reached this state.
    """

    return (rm.state == game.room.state.tutorial and u.state == game.room.state.pve) or \
        (rm.state == game.room.state.pve and u.state == game.room.state.pvp)


def get_opponent_progression(u, rd_opp):
    """
    :return: The percentage of opponent progression
     in the previous round
    """

    if u.state == game.room.state.pve:
        progression = u.tutorial_progression

    else:
        if rd_opp.state == game.room.state.pve:
            progression = (rd_opp.t / rd_opp.ending_t) * 100
        else:
            progression = 100

    return str(rnd(progression))


def go_to_next_round(u, opp, rm):

    if rm.state == game.room.state.tutorial and u.state == game.room.state.tutorial:
        _tutorial_is_done(u=u, opp=opp, rm=rm)

    elif rm.state == game.room.state.pve and u.state == game.room.state.pve:
        _pve_is_done(u=u, opp=opp, rm=rm)

    elif rm.state == game.room.state.pvp and u.state == game.room.state.pvp:
        _pvp_is_done(u=u, opp=opp, rm=rm)


def _tutorial_is_done(u, opp, rm):

    # change player.state
    u.state = game.room.state.pve
    u.save(update_fields=("state",))

    # if other player has done tutorial, set rm.state to pve
    if rm.trial or opp.state == game.room.state.pve:
        rm.state = game.room.state.pve
        rm.save(update_fields=("state",))


def _pve_is_done(u, opp, rm):

    # load objects
    next_round = Round.objects.get(id=u.room_id, state=game.room.state.pvp)
    next_role = RoundComposition.objects.get(round_id=next_round.id, user_id=u.id)

    # player is assigned to next round id
    u.round_id = next_round.id
    u.firm_id = next_role.firm_id
    u.state = game.room.state.pvp
    u.save(update_fields=("state",))

    # set room state
    if rm.trial or opp.state == game.room.state.pvp:

        rm.state = game.room.state.pvp
        rm.save(update_fields=("state", ))


def _pvp_is_done(u, opp, rm):

    # Modify sate of player
    u.state = game.room.state.end
    u.save(update_fields=("state", ))

    if rm.trial or opp.state == game.room.state.end:

        # Close room and set state
        rm.opened = False
        rm.state = game.room.state.end
        rm.save(update_fields=("opened", "state"))
