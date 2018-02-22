import os

from utils import utils
from parameters import parameters

from game.models import Players, RoundState, Round, RoundComposition

from . import data, state
from game import player, room

__path__ = os.path.relpath(__file__)


"""
    Here are grouped the functions called by: game.views (i.e. by client)
"""


# ----------------------------------- Ask functions ------------------------------------------------------ #
def ask_firm_init(player_id):

    # -------  Get needed objects  ----------------------------------------------------------------- #

    p = Players.objects.get(player_id=player_id)
    rd = Round.objects.get(round_id=p.round_id)

    # -------  Log stuff -------------------------------------------------------------------------- #

    utils.log("Player {} for room {} and round {} ask init: t is {}.".format(
        player_id, p.room_id, rd.round_id, rd.t),
        f=utils.fname(), path=__path__)

    # -------  Maybe client has to wait the other player ------------------------------------------ #

    if player.dialog.client_has_to_wait_over_player(player_id=player_id, called_from=utils.fname()):

        if not room.dialog.is_trial(player_id, utils.fname()):

            opp_progression = player.dialog.get_opponent_progression(
                player_id=player_id,
                called_from=utils.fname()
            )
            return parameters.error["wait"], opp_progression  # Tuple is necessary!! '-1' hold for wait

    # Get information necessary for firm initialization
    d = data.get_init_info(player_id=player_id)

    return rd.t, d["firm_state"], d["player"]["position"], d["player"]["price"], d["player"]["profits"], \
        d["opp"]["position"], d["opp"]["price"], d["opp"]["profits"], rd.ending_t


# ----------------------------------| passive firm demands |-------------------------------------- #

def ask_firm_passive_opponent_choice(player_id, t):

    # -------  Get needed objects  ----------------------------------------------------------------- #

    p = Players.objects.get(player_id=player_id)
    rd = Round.objects.get(round_id=p.round_id)

    # -------  Get needed variables --------------------------------------------------------------- #

    agent_id = RoundComposition.objects.get(round_id=rd.round_id, player_id=player_id).agent_id
    opponent_id = (agent_id + 1) % parameters.n_firms

    # -------  Log stuff -------------------------------------------------------------------------- #
    utils.log("Firm passive {} of room {} and round {} asks for opponent strategy.".format(
        player_id, p.room_id, rd.round_id
    ),
        f=utils.fname(), path=__path__)

    utils.log(
        "Client's time is {}, server's time is {}.".format(t, rd.t),
        f=utils.fname(), path=__path__
    )

    # ---------- Record call ------------------------------------------------------------------ #

    if t <= rd.t:

        # Make bot firm play if applicable
        if state.check_if_bot_firm_has_to_play(rd.round_id, t):
            state.check_if_consumers_have_to_play(round_id=rd.round_id, t=t)

        # Get the state (possibly new)
        rs = RoundState.objects.get(round_id=rd.round_id, t=t)

        if rs.firm_active_played:
            positions, prices = data.get_positions_and_prices(round_id=rd.round_id, t=t)
            return t, positions[opponent_id], prices[opponent_id]

        else:
            utils.log("Have to wait: Active firm needs to play", f=utils.fname(), path=__path__)
            return parameters.error["wait"],  # Tuple is necessary!!

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


def ask_firm_passive_consumer_choices(player_id, t):

    # -------  Get needed objects  ----------------------------------------------------------------- #
    p = Players.objects.get(player_id=player_id)
    rd = Round.objects.get(round_id=p.round_id)
    rs = RoundState.objects.get(round_id=rd.round_id, t=t)

    agent_id = RoundComposition.objects.get(round_id=rd.round_id, player_id=player_id).agent_id
    # -------  Log stuff -------------------------------------------------------------------------- #

    utils.log("Firm {} (passive) of room {} and round {} asks for its number of clients.".format(
        agent_id, p.room_id, rd.round_id
    ),
        f=utils.fname(),
        path=__path__
    )

    utils.log(
        "Client's time is {}, server's time is {}.".format(t, rd.t), f=utils.fname(), path=__path__)

    # ---------- Do stuff ------------------------------------------------------------------- #

    if t <= rd.t:

        if rs.consumers_played:

            is_end = int(state.is_end_of_game(round_id=rd.round_id, t=t))

            consumer_choices = data.get_consumer_choices(round_id=rd.round_id, t=t)
            consumer_choices = [1 if i == agent_id else 0 if i != -1 else -1 for i in consumer_choices]

            if is_end:
                player.dialog.go_to_next_round(player_id=player_id, called_from=utils.fname())

            return (t, ) + tuple((i for i in consumer_choices)) + (is_end, )

        else:
            return parameters.error["wait"],   # Tuple is necessary!! // Have to wait

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


# -----------------------------------| active firm demands |-------------------------------------- #

def ask_firm_active_choice_recording(player_id, t, position, price):

    # -------  Get needed objects  --------------------------------------------------------------- #

    p = Players.objects.get(player_id=player_id)
    rd = Round.objects.get(round_id=p.round_id)
    rs = RoundState.objects.get(round_id=rd.round_id, t=t)
    rc = RoundComposition.objects.get(round_id=rd.round_id, player_id=p.player_id)

    # -------  Log stuff ------------------------------------------------------------------------- #
    utils.log(
        "Firm active {} of room {} and round {} asks to save its price and position.".format(
            player_id, p.room_id, rd.round_id
        ), f=utils.fname(), path=__path__)

    utils.log(
        "Client's time is {}, server's time is {}.".format(t, rd.t),
        f=utils.fname(), path=__path__)

    # -------  do stuff -------------------------------------------------------------------------- #

    assert rc.agent_id == rc.agent_id, "Non matching agent_id == agent_id"

    if t <= rd.t:

        if not rs.firm_active_played:

            data.register_firm_choices(
                round_id=rd.round_id,
                agent_id=rc.agent_id,
                t=t,
                position=position,
                price=price
            )

            state.check_if_consumers_have_to_play(round_id=rd.round_id, t=t)

        return t,  # ! Must be a tuple

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


def ask_firm_active_consumer_choices(player_id, t):

    # -------  Get needed objects  ---------------------------------------------------------------- #

    p = Players.objects.get(player_id=player_id)
    rd = Round.objects.get(round_id=p.round_id)
    rs = RoundState.objects.get(round_id=rd.round_id, t=t)

    # -------  Get needed variables --------------------------------------------------------------- #

    agent_id = RoundComposition.objects.get(round_id=rd.round_id, player_id=player_id).agent_id

    # -------  Log stuff -------------------------------------------------------------------------- #

    utils.log(
        "Firm active {} of room {} and round {} asks the number of its clients.".format(
            player_id, p.room_id, rd.round_id
        ), f=utils.fname(), path=__path__)
    utils.log("Client's time is {}, server's time is {}.".format(t, rd.t), f=utils.fname(), path=__path__)

    # ---------------- Do stuff ------------------------------------------ #

    if t <= rd.t:

        is_end = int(state.is_end_of_game(round_id=rd.round_id, t=t))

        if rs.firm_active_played:

            consumer_choices = data.get_consumer_choices(round_id=rd.round_id, t=t)
            consumer_choices = [1 if i == agent_id else 0 if i != -1 else -1 for i in consumer_choices]

            if is_end:
                player.dialog.go_to_next_round(player_id=player_id, called_from=utils.fname())

            return (t,) + tuple((i for i in consumer_choices)) + (is_end,)

        else:
            return parameters.error["wait"],  # Tuple is necessary!!

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!
