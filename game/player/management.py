import utils.utils as utils
from parameters import parameters
from builtins import round as rnd
import datetime
from django.utils import timezone

from game.models import Round, Room, Players, RoundComposition, RoundState, Users
from dashboard.models import IntParameters

from game import room, tutorial, round

from . import bots


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
        progression = \
            tutorial.dialog.get_tutorial_progression(player_id=opp.player_id)
    else:
        comp = RoundComposition.objects.filter(player_id=opp.player_id)
        rd = None

        for c in comp:
            rd = Round.objects.get(round_id=c.round_id)
            if rd.state == room.state.pve:
                break

        progression = (rd.t / rd.ending_t) * 100

    return str(rnd(progression))


def check_if_bot_firm_has_to_play(round_id, t):

    # Log
    utils.log("Called", f=utils.function_name(), path=__path__)

    # Get round
    rd = Round.objects.filter(round_id=round_id).first()

    # Check if round contains bots
    if rd.real_players < parameters.n_firms:

        # Get round state
        round_state = RoundState.objects.get(round_id=round_id, t=t)

        # Get firm bot
        firm_bot = RoundComposition.objects.filter(round_id=round_id, bot=1, role="firm").first()

        # If active firm did not play and bot firms not already played
        if firm_bot.agent_id == round_state.firm_active \
                and not round_state.firm_active_played:

            bots.firm.play(round_id=round_id, t=t)

            round_state.firm_active_played = 1

            round_state.save(force_update=True)

            utils.log("Bot firm played.",
                      f=utils.function_name(), path=__path__)

            return True

        else:
            utils.log("Bot firm has already played (or is not active).",
                      f=utils.function_name(), path=__path__)

    else:
        utils.log("Round does not contain bots.", f=utils.function_name(), path=__path__)

    return False


def check_if_consumers_have_to_play(round_id, t):

    # Log
    utils.log("Called", f=utils.function_name(), path=__path__)

    # Get room state
    round_state = RoundState.objects.get(round_id=round_id, t=t)

    # Then consumers need to choose a perimeter as well as a firm to buy from
    if round_state.firm_active_played and not round_state.consumers_played:

        bots.consumer.play(round_id=round_id, t=t)

        round_state.consumers_played = 1
        round_state.save(force_update=True)

        round.dialog.compute_scores(round_id=round_id, t=t)
        round.dialog.advance_of_one_time_step(round_id=round_id, t=t)
        return True

    else:
        return False


def go_to_next_round(player_id):

    p = Players.objects.get(player_id=player_id)
    room_id = Round.objects.get(round_id=p.round_id).room_id
    room_state = Room.objects.get(room_id=room_id).state

    utils.log("Going to next round: room.state = {}".format(room_state), f=utils.function_name(), path=__path__)

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
        room.dialog.update_state(room_id=rm.room_id, room_state=room.state.pve)


def _pve_is_done(player_id):

    p = Players.objects.get(player_id=player_id)

    # As player is alone, once he finished, we can close the r
    round.dialog.close_round(round_id=p.round_id)

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
        room.dialog.update_state(room_id=p.room_id, room_state=room.state.pvp)


def _pvp_is_done(player_id):

    p = Players.objects.get(player_id=player_id)

    # Modify sate of player
    p.state = room.state.end
    p.save(force_update=True)

    rm = Room.objects.get(room_id=p.room_id)

    if rm.trial or _opponent_has_done_pvp(player_id=player_id):

        # Close round
        round.dialog.close_round(round_id=p.round_id)

        # Close room and set state
        room.dialog.close(room_id=p.room_id, called_from=__path__ + ":" + utils.function_name())
        room.dialog.update_state(room_id=p.room_id, room_state=room.state.end)


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


def set_time_last_request(player_id, function_name):
    """
    called by game.views
    """

    player = Players.objects.get(player_id=player_id)
    player.time_last_request = timezone.now()
    player.last_request = function_name
    player.save(force_update=True)


def banned(f):
    """
    decorator used in game.round.client
    in order to check if opponent/player is still playing
    or is AFK
    """
    def new_f(request):

        player_id = request.POST["player_id"]
        opp_id = get_opponent_player_id(player_id)

        # check if trial (if trial we do not want to ban players)
        trial = room.dialog.is_trial(player_id)
        # check if room is not in end state (meaning we
        # do not want to ban players because they already
        # completed the game but have tried to reconnect)

        p = Players.objects.get(player_id=player_id)
        already_ended = room.dialog.get_state(room_id=p.room_id) == room.state.end

        if not trial and not already_ended:

            if _player_has_quit(player_id):
                utils.log(
                    "The current player is a deserter.",
                    f=f.__name__,
                    path=__path__,
                    level=3
                )
                return "reply", f.__name__, parameters.error["player_quit"]

            elif opp_id and _player_has_quit(opp_id):
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


def _player_has_quit(player_id):

    p = Players.objects.get(player_id=player_id)
    rm = Room.objects.get(room_id=p.room_id)

    # First get time of the last request
    t_last_request = p.time_last_request
    # Then get the timezone
    tz_info = p.time_last_request.tzinfo
    # Get time now using timezone info
    t_now = datetime.datetime.now(tz_info)
    # Generate a timedelta
    minutes = IntParameters.objects.get(name="disconnected_timeout").value
    five_min = datetime.timedelta(minutes=minutes)
    # If more than 5 min since the last request
    has_quit = t_now > t_last_request + five_min
    # Set the opponent as a deserter
    # and return that info to the player
    u = Users.objects.get(player_id=p.player_id)
    u.deserter = int(has_quit)
    u.save(force_update=True)
    # If there is a deserter, close the concerned room
    if has_quit:
        room.dialog.close(room_id=rm.room_id, called_from=__path__+":"+utils.function_name())

    return has_quit
