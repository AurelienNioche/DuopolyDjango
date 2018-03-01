from utils import utils

from game.models import Round, RoundComposition

import game.round.data
import game.room.state


def end_of_turn(rd, rs, t):

    rs.firm_active_and_consumers_played = True
    rs.save(update_fields=["firm_active_and_consumers_played"])

    game.round.data.compute_scores(rd=rd, t=t)

    if not is_end_of_round(rd, t):
        rd.t += 1
        rd.save(update_fields=["t"])


def is_end_of_round(rd, t):

    utils.log("ending_t: {}, t: {}".format(rd.ending_t, t), f=is_end_of_round)

    return t == rd.ending_t - 1  # -1 because starts at 0


def client_has_to_wait_over_player(u, opp, rm):
    """
    Check if player state is more advanced than the room state.
    The room state is changed only if both players reached this state.
    """

    if u.state == game.room.state.pve and (not opp or opp.state == game.room.state.pve):

        if rm.state == game.room.state.tutorial:
            rm.state = game.room.state.pve
            rm.save(update_fields=["state"])
        return False

    elif u.state == game.room.state.pvp and (not opp or opp.state == game.room.state.pvp):

        if rm.state == game.room.state.pve:
            rm.state = game.room.state.pvp
            rm.save(update_fields=["state"])

        return False

    return True


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

    return str(round(progression))


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
    u.save(update_fields=["state"])

    # if other player has done tutorial, set rm.state to pve
    if rm.trial or opp.state == game.room.state.pve:
        rm.state = game.room.state.pve
        rm.save(update_fields=["state"])


def _pve_is_done(u, opp, rm):

    utils.log("User {} has done pve. I will put him in pvp.", f=_pve_is_done)

    # load objects
    next_round = Round.objects.get(room_id=u.room_id, pvp=True)
    next_role = RoundComposition.objects.get(round_id=next_round.id, user_id=u.id)

    # player is assigned to next round id
    u.round_id = next_round.id
    u.firm_id = next_role.firm_id
    u.state = game.room.state.pvp
    u.save(update_fields=["round_id", "firm_id", "state"])

    # set room state
    if rm.trial or opp.state == game.room.state.pvp:

        rm.state = game.room.state.pvp
        rm.save(update_fields=["state"])


def _pvp_is_done(u, opp, rm):

    # Modify sate of player
    u.state = game.room.state.end
    u.save(update_fields=["state"])

    if rm.trial or opp.state == game.room.state.end:

        # Close room and set state
        rm.opened = False
        rm.state = game.room.state.end
        rm.save(update_fields=["opened", "state"])
