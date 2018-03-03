import datetime
from django.utils import timezone

from dashboard.models import IntParameter

from utils import utils
from parameters import parameters

import game.room.state


def check(demand, users, u, opp=None, rm=None):
    """
    decorator used in game.round.client
    in order to check if opponent/player is connected
    or is AFK
    """

    # Refresh  list of connected users
    check_connected_users(users=users)

    # # ----------  If user has not signed up ----------------- #
    if not u:
        return

    _set_time_last_request(u=u, function_name=demand)

    # # ----------  If user has not joined a room yet ----------------- #
    if not u.registered:
        return

    # ----------  If user has joined a room ------------------------- #

    # check if room is not in end state (meaning we
    # do not want to ban players because they already
    # completed the game but have tried to reconnect)

    if rm is not None and not rm.trial and not rm.state == game.room.state.end:

        # First, we check that the function called is missing players
        # if we reach the missing opponent timeout then return error
        if demand == "missing_players" and _no_opponent_found(u=u, rm=rm):
            utils.log("No opponent has been found for {}".format(u.username), f=check, level=3)
            return parameters.error["no_opponent_found"]

        # Then, we check that the current player is not
        # a deserter
        if banned(u=u, rm=rm):
            utils.log("{} is a deserter.".format(u.username), f=check, level=3)
            return parameters.error["player_quit"]

        # If the player is not a deserter, we can save its last request
        _set_time_last_request(u, demand)

        # Then, we check if the opponent has reached banishment timeout
        if opp and banned(u=opp, rm=rm):
            utils.log("{} is a deserter.".format(u.username), f=check, level=3)
            return parameters.error["opponent_quit"]


def check_connected_users(users):

    for u in users:
        connected = not _is_timed_out(u.time_last_request, "disconnected_timeout")
        if connected != u.connected:
            u.connected = connected
            u.save(update_fields=["connected"])


def banned(u, rm):

    if _is_timed_out(u.time_last_request, "banishment_timeout"):

        # Set the opponent as a deserter
        # and return that info to the player
        u.deserter = True
        u.save(update_fields=["deserter"])

        rm.opened = False
        rm.save(update_fields=["opened"])

        return True

    else:
        return False


def _is_timed_out(reference_time, timeout_parameter):

    # Then get the timezone
    tz_info = reference_time.tzinfo
    # Get time now using timezone info
    t_now = datetime.datetime.now(tz_info)
    # Generate a timedelta
    param = IntParameter.objects.filter(name=timeout_parameter).first()
    if param is None:

        if timeout_parameter == "no_opponent_timeout":
            param = IntParameter(name=timeout_parameter, value=15, unit="minutes")
            param.save()
        elif timeout_parameter == "disconnected_timeout":
            param = IntParameter(name=timeout_parameter, value=30, unit="seconds")
            param.save()
        else:
            param = IntParameter(name=timeout_parameter, value=15, unit="minutes")
            param.save()

    if param.unit == "seconds":
        delta = datetime.timedelta(seconds=param.value)
    else:
        delta = datetime.timedelta(minutes=param.value)

    # If more than X min/seconds since the last request
    timeout = t_now > reference_time + delta

    return timeout


def _set_time_last_request(u, function_name):
    """
    called by game.views via player.client
    """

    u.time_last_request = timezone.now()
    u.last_request = function_name
    u.save(update_fields=["time_last_request", "last_request"])


def _no_opponent_found(u, rm):

    not_found = rm.missing_players and _is_timed_out(u.registration_time, "no_opponent_timeout")

    if not_found:
        rm.opened = False
        rm.save(update_fields=["opened"])

    return not_found
