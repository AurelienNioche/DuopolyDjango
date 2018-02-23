import os
from builtins import round as rnd
import datetime
from django.utils import timezone

from game.models import Round, Room, Players, RoundComposition, Users
from dashboard.models import IntParameters

from utils import utils
from parameters import parameters
from game import room, tutorial, round


__path__ = os.path.relpath(__file__)


def client_has_to_wait_over_player(player_id):
    """
    Check if player state is more advanced than the room state.
    The room state is changed only if both players reached this state.
    :param player_id: int
    :return: boolean
    """

    p = Players.objects.get(player_id=player_id)
    rm = Room.objects.get(room_id=p.room_id)

    return (rm.state == room.state.tutorial and p.state == room.state.pve) or \
        (rm.state == room.state.pve and p.state == room.state.pvp)


def get_opponent_progression(player_id):
    """
    :return: The percentage of opponent progression
     in the previous round
    """

    p = Players.objects.get(player_id=player_id)
    opp = Players.objects.filter(room_id=p.room_id).exclude(player_id=player_id).first()

    if p.state == room.state.pve:
        progression = tutorial.dialog.get_tutorial_progression(
                player_id=opp.player_id,
                called_from=__path__ + ':' + utils.fname()
            )
    else:
        comp = RoundComposition.objects.filter(player_id=opp.player_id)
        rd = None

        for c in comp:
            rd = Round.objects.get(round_id=c.round_id)
            if rd.state == room.state.pve:
                break

        progression = (rd.t / rd.ending_t) * 100

    return str(rnd(progression))


def go_to_next_round(player_id):

    p = Players.objects.get(player_id=player_id)
    room_id = Round.objects.get(round_id=p.round_id).room_id
    room_state = Room.objects.get(room_id=room_id).state

    utils.log("Going to next round: room.state = {}".format(room_state), f=utils.fname(), path=__path__)

    if room_state == room.state.tutorial and p.state == room.state.tutorial:
        _tutorial_is_done(player_id=player_id)

    elif room_state == room.state.pve and p.state == room.state.pve:
        _pve_is_done(player_id=player_id)

    elif room_state == room.state.pvp and p.state == room.state.pvp:
        _pvp_is_done(player_id=player_id)

    else:
        return False

    return True


def _tutorial_is_done(player_id):

    # change player.state
    p = Players.objects.get(player_id=player_id)
    p.state = room.state.pve
    p.save(force_update=True)

    rm = Room.objects.get(room_id=p.room_id)

    # if other player has done tutorial, set rm.state to pve
    if rm.trial or _opponent_has_done_tutorial(player_id=player_id):

        room.dialog.update_state(
            room_id=rm.room_id,
            room_state=room.state.pve,
            called_from=__path__ + ':' + utils.fname()
        )


def _pve_is_done(player_id):

    p = Players.objects.get(player_id=player_id)

    # As player is alone, once he finished, we can close the r
    round.dialog.close_round(round_id=p.round_id, called_from=__path__ + ':' + utils.fname())

    # load objects
    next_round = Round.objects.get(room_id=p.room_id, state=room.state.pvp)
    player = Players.objects.get(player_id=player_id)
    rm = Room.objects.get(room_id=p.room_id)

    # player is assigned to next round id
    player.round_id = next_round.round_id
    player.state = room.state.pvp
    player.save(force_update=True)

    # set room state
    if rm.trial or _opponent_has_done_pve(player_id=player_id):
        room.dialog.update_state(room_id=p.room_id, room_state=room.state.pvp, called_from=__path__ + ':' + utils.fname())


def _pvp_is_done(player_id):

    p = Players.objects.get(player_id=player_id)

    # Modify sate of player
    p.state = room.state.end
    p.save(force_update=True)

    rm = Room.objects.get(room_id=p.room_id)

    if rm.trial or _opponent_has_done_pvp(player_id=player_id):

        # Close round
        round.dialog.close_round(round_id=p.round_id, called_from=__path__ + ':' + utils.fname())

        # Close room and set state
        room.dialog.close(room_id=p.room_id, called_from=__path__ + ":" + utils.fname())
        room.dialog.update_state(room_id=p.room_id, room_state=room.state.end, called_from=__path__ + ':' + utils.fname())


# --------------------------------------- Info regarding the opponent --------------------------------------------- #


def _opponent_has_done_pve(player_id):

    p = Players.objects.get(player_id=player_id)

    opponent_state = \
        Players.objects.filter(room_id=p.room_id).exclude(player_id=player_id).first().state
    return opponent_state == room.state.pvp


def _opponent_has_done_pvp(player_id):

    p = Players.objects.get(player_id=player_id)

    opponent_state = \
        Players.objects.filter(room_id=p.room_id).exclude(player_id=player_id).first().state
    return opponent_state == room.state.end


def _opponent_has_done_tutorial(player_id):

    p = Players.objects.get(player_id=player_id)

    opponent_state = \
        Players.objects.filter(room_id=p.room_id).exclude(player_id=player_id).first().state
    return opponent_state == room.state.pve


# --------------------------------------- Info regarding time and disconnection ------------------------------------- #


def _set_time_last_request(player_id, function_name, username=None):
    """
    called by game.views via player.client
    """

    if username:
        user = Users.objects.get(username=username)
    else:
        user = Users.objects.get(player_id=player_id)

    user.time_last_request = timezone.now()
    user.last_request = function_name
    user.save(force_update=True)


def connection_checker(f):
    """
    decorator used in game.round.client
    in order to check if opponent/player is connected
    or is AFK
    """
    def new_f(request):

        decorator_name = "player.management.connection_checker"
        player_id = request.POST.get("player_id")
        username = request.POST.get("username")

        # Refresh  list of connected users
        check_connected_users()

        # ----------  If user has not joined a room yet ----------------- #
        if username:
            _set_time_last_request(None, f.__name__, username=username)
            return f(request)

        # ----------  If user has joined a room ------------------------- #

        # check if trial (if trial we do not want to ban player
        trial = room.dialog.is_trial(player_id, called_from=decorator_name)

        # check if room is not in end state (meaning we
        # do not want to ban players because they already
        # completed the game but have tried to reconnect)
        p = Players.objects.get(player_id=player_id)
        already_ended = \
            room.dialog.get_state(room_id=p.room_id, called_from=decorator_name) == room.state.end

        if not trial and not already_ended:

            # First, we check that the function called is missing players
            # if we reach the missing opponent timeout then return error
            if f.__name__ == "missing_players" and _no_opponent_found(player_id):

                return "reply", f.__name__, parameters.error["no_opponent_found"]

            # Then, we check that the current player is not
            # a deserter
            if _player_is_banned(player_id):
                utils.log(
                    "The current player is a deserter.",
                    f=f.__name__,
                    path=__path__,
                    level=3
                )
                return "reply", f.__name__, parameters.error["player_quit"]

            # If the player is not a deserter, we can save its last request
            _set_time_last_request(player_id, f.__name__)

            # Then, we check if the opponent has reached banishment timeout
            opp_id = get_opponent_player_id(player_id)
            if opp_id and _player_is_banned(opp_id):
                utils.log(
                    "The other player is a deserter.",
                    f=f.__name__,
                    path=__path__,
                    level=3
                )
                return "reply", f.__name__, parameters.error["opponent_quit"]

        return f(request)

    return new_f


def get_opponent_player_id(player_id):
    """
    called by round.state.player_has_quit
    """
    current_player = Players.objects.get(player_id=player_id)
    opp = Players.objects.filter(room_id=current_player.room_id).exclude(player_id=player_id).first()

    return opp.player_id if opp else None


def _player_is_banned(player_id):

    u = Users.objects.get(player_id=player_id)
    p = Players.objects.get(player_id=player_id)
    rm = Room.objects.get(room_id=p.room_id)

    if _is_timed_out(u.time_last_request, "banishment_timeout"):

        # Set the opponent as a deserter
        # and return that info to the player
        u.deserter = 1
        u.save(force_update=True)

        room.dialog.close(room_id=rm.room_id, called_from=__path__+":"+utils.fname())

        return True


def check_connected_users():

    for u in Users.objects.all():
        u.connected = int(_is_timed_out(u.time_last_request, "disconnected_timeout"))
        u.save(force_update=True)


def _no_opponent_found(player_id):

    p = Players.objects.get(player_id=player_id)
    rm = Room.objects.get(room_id=p.room_id)

    return rm.missing_players and _is_timed_out(p.registration_time, "no_opponent_timeout")


def _is_timed_out(reference_time, timeout_parameter):

    # Then get the timezone
    tz_info = reference_time.tzinfo
    # Get time now using timezone info
    t_now = datetime.datetime.now(tz_info)
    # Generate a timedelta
    minutes = IntParameters.objects.get(name=timeout_parameter).value
    minutes_delta = datetime.timedelta(minutes=minutes)

    # If more than X min since the last request
    timeout = t_now > reference_time + minutes_delta

    return timeout







