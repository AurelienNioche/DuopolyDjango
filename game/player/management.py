import os
from builtins import round as rnd
import datetime
from django.utils import timezone

from game.models import Round, RoundComposition
from dashboard.models import IntParameters

from utils import utils
from parameters import parameters
from game import room, round


__path__ = os.path.relpath(__file__)


def client_has_to_wait_over_player(u, rm):
    """
    Check if player state is more advanced than the room state.
    The room state is changed only if both players reached this state.
    :param player_id: int
    :return: boolean
    """

    return (rm.state == room.state.tutorial and u.state == room.state.pve) or \
        (rm.state == room.state.pve and u.state == room.state.pvp)


def get_opponent_progression(u, opp):
    """
    :return: The percentage of opponent progression
     in the previous round
    """

    if u.state == room.state.pve:
        progression = u.tutorial_progression
    else:
        comp = RoundComposition.objects.filter(player_id=opp.id)
        rd = None

        for c in comp:
            rd = Round.objects.get(round_id=c.round_id)
            if rd.state == room.state.pve:
                break

        progression = (rd.t / rd.ending_t) * 100

    return str(rnd(progression))


def go_to_next_round(p, rd, rm):

    # p = Players.objects.get(player_id=player_id)
    # room_id = Round.objects.get(round_id=p.round_id).room_id
    # room_state = Room.objects.get(room_id=room_id).state

    utils.log("Going to next round: room.state = {}".format(rm.room_state), f=utils.fname(), path=__path__)

    if rm.room_state == room.state.tutorial and p.state == room.state.tutorial:
        _tutorial_is_done(p, rm)

    elif rm.room_state == room.state.pve and p.state == room.state.pve:
        _pve_is_done(p=p, rm=rm)

    elif rm.room_state == room.state.pvp and p.state == room.state.pvp:
        _pvp_is_done(p=p, rm=rm)

    else:
        return False

    return True


def _tutorial_is_done(p, opp, rm):

    # change player.state
    p.state = room.state.pve
    p.save()

    # if other player has done tutorial, set rm.state to pve
    if rm.trial or opp.state == room.state.pve:

        room.dialog.update_state(
            room_id=rm.room_id,
            room_state=room.state.pve,
            called_from=__path__ + ':' + utils.fname()
        )


def _pve_is_done(p, opp, rm):

    # load objects
    next_round = Round.objects.get(room_id=p.room_id, state=room.state.pvp)

    # player is assigned to next round id
    p.round_id = next_round.round_id
    p.state = room.state.pvp
    p.save()

    # set room state
    if opp.state == room.state.pvp:

        rm.state = room.state.pvp
        rm.save()

        # room.dialog.update_state(
        #     room_id=p.room_id, room_state=room.state.pvp, called_from=__path__ + ':' + utils.fname())


def _pvp_is_done(p, opp, rm):

    # Modify sate of player
    p.state = room.state.end
    p.save()

    if opp.state == room.state.end:

        # Close room and set state
        room.dialog.close(rm=rm, called_from=__path__ + ":" + utils.fname())

        rm.state = room.state.end
        rm.save()

        # room.dialog.update_state(rm=rm, room_state=room.state.end, called_from=__path__ + ':' + utils.fname())


# --------------------------------------- Info regarding time and disconnection ------------------------------------- #


def _set_time_last_request(u, function_name):
    """
    called by game.views via player.client
    """

    u.time_last_request = timezone.now()
    u.last_request = function_name
    u.save()


def connection_checker(called_from, users, p=None, opp=None, rm=None, username=None):
    """
    decorator used in game.round.client
    in order to check if opponent/player is connected
    or is AFK
    """

    # Refresh  list of connected users
    check_connected_users(users=users)

    if username:
        u = users.filter(username=username).first()
    else:
        u = users.filter(player_id=p.player_id).first()

    # # ----------  If user has not joined a room yet ----------------- #
    if username:
        _set_time_last_request(u=u, called_from=called_from)
        return True

    # ----------  If user has joined a room ------------------------- #

    # check if room is not in end state (meaning we
    # do not want to ban players because they already
    # completed the game but have tried to reconnect)
    # p = Players.objects.get(player_id=player_id)

    # already_ended = \
    #     room.dialog.get_state(rm=rm, called_from=connection_checker.__name__) == room.state.end

    if not rm.trial and not rm.state.end:

        # First, we check that the function called is missing players
        # if we reach the missing opponent timeout then return error
        if called_from == "missing_players" and _no_opponent_found(p=p, rm=rm):

            return True, parameters.error["no_opponent_found"]

        # Then, we check that the current player is not
        # a deserter
        if player_is_banned(u=u, rm=rm):
            utils.log(
                "The current player is a deserter.",
                f=connection_checker.__name__,
                path=__path__,
                level=3
            )
            return True, parameters.error["player_quit"]

        # If the player is not a deserter, we can save its last request
        _set_time_last_request(u, called_from)

        # Then, we check if the opponent has reached banishment timeout
        opp_id = opp.player_id if opp else None
        if opp_id and player_is_banned(opp_id):
            utils.log(
                "The other player is a deserter.",
                f=connection_checker.__name__,
                path=__path__,
                level=3
            )
            return False, parameters.error["opponent_quit"]
    else:
        return True


def player_is_banned(u, rm):

    # u = Users.objects.filter(player_id=player_id).first()
    #
    # if u is not None:
    #
    # p = Players.objects.get(player_id=player_id)
    # rm = Room.objects.get(room_id=p.room_id)

    if _is_timed_out(u.time_last_request, "banishment_timeout"):

        # u = Users.objects.get(player_id=player_id)

        # Set the opponent as a deserter
        # and return that info to the player
        u.deserter = 1
        u.save()

        room.dialog.close(rm=rm, called_from=__path__+":"+utils.fname())

        return True
    
    else:
        return False


def check_connected_users(users):

    for u in users:
        u.connected = int(not _is_timed_out(u.time_last_request, "disconnected_timeout"))
        u.save()


def _no_opponent_found(p, rm):

    not_found = rm.missing_players and _is_timed_out(p.registration_time, "no_opponent_timeout")

    if not_found:
        room.dialog.close(room_id=rm.room_id, called_from=__path__+":"+utils.fname())

    return not_found


def _is_timed_out(reference_time, timeout_parameter):

    # Then get the timezone
    tz_info = reference_time.tzinfo
    # Get time now using timezone info
    t_now = datetime.datetime.now(tz_info)
    # Generate a timedelta
    param = IntParameters.objects.filter(name=timeout_parameter).first()
    if param is None:

        if timeout_parameter == "no_opponent_timeout":
            param = IntParameters(name=timeout_parameter, value=15, unit="minutes")
            param.save()
        elif timeout_parameter == "disconnected_timeout":
            param = IntParameters(name=timeout_parameter, value=30, unit="seconds")
            param.save()
        else:
            param = IntParameters(name=timeout_parameter, value=15, unit="minutes")
            param.save()

    if param.unit == "seconds":
        delta = datetime.timedelta(seconds=param.value)
    else:
        delta = datetime.timedelta(minutes=param.value)

    # If more than X min/seconds since the last request
    timeout = t_now > reference_time + delta

    return timeout
