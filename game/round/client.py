import os

from utils import utils
from parameters import parameters

from game.models import RoundComposition


import game.round.bots.firm
import game.round.bots.consumer
import game.round.state
import game.round.data

__path__ = os.path.relpath(__file__)

"""
    Here are grouped the functions called by client during the playing phase
"""


# ----------------------------------- init ------------------------------------------------------ #

def ask_firm_init(u, rd_opp, rm, rd, rs):

    # Maybe client has to wait the other player
    if game.round.state.client_has_to_wait_over_player(u=u, rm=rm):

        if not rm.trial:
            opp_progression = game.round.state.get_opponent_progression(u=u, rd_opp=rd_opp)
            return parameters.error["wait"], opp_progression  # Tuple is necessary!! '-1' hold for wait

    # Get information necessary for firm initialization
    d = game.round.data.get_init_info(u=u, rd=rd, rs=rs)

    return rd.t, d["firm_state"], d["player"]["position"], d["player"]["price"], d["player"]["profits"], \
        d["opp"]["position"], d["opp"]["price"], d["opp"]["profits"], rd.ending_t


# ----------------------------------| passive firm demands |-------------------------------------- #

def ask_firm_passive_opponent_choice(u, rd, rs, t):

    if t <= rd.t:

        # Get firm bot if there is one
        firm_bot = RoundComposition.objects.filter(round_id=rd.id, bot=True).first()

        # Make bot firm play if applicable
        if firm_bot and game.round.bots.firm.play(firm_bot=firm_bot, rd=rd, rs=rs, t=t):
            game.round.bots.consumer.play(rd=rd, t=t)
            game.round.state.end_of_turn(rd=rd, rs=rs, t=t)

        if rs.firm_active_and_consumers_played:
            opponent_id = (u.firm_id + 1) % parameters.n_firms
            positions, prices = game.round.data.get_positions_and_prices(rd=rd, t=t)
            return t, positions[opponent_id], prices[opponent_id]

        else:
            utils.log("Have to wait: Active firm needs to play", f=utils.fname(), path=__path__)
            return parameters.error["wait"],  # Tuple is necessary!!

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


def ask_firm_passive_consumer_choices(u, opp, rm, rd, rs, t):

    if t <= rd.t:

        if rs.firm_active_and_consumers_played:

            round_ends = int(game.round.state.is_end_of_round(rd=rd, t=t))

            consumer_choices = game.round.data.get_consumer_choices(rd=rd, t=t)
            consumer_choices = [1 if i == u.firm_id else 0 if i != -1 else -1 for i in consumer_choices]

            if round_ends:
                game.round.state.go_to_next_round(u=u, opp=opp, rm=rm)

            return (t,) + tuple((i for i in consumer_choices)) + (round_ends,)

        else:
            utils.log("Have to wait: Active firm needs to play", f=utils.fname(), path=__path__)
            return parameters.error["wait"],  # Tuple is necessary!! // Have to wait

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


# -----------------------------------| active firm demands |-------------------------------------- #

def ask_firm_active_choice_recording(u, rd, rs, t, position, price):

    if t <= rd.t:

        if not rs.firm_active_played:
            # tables FirmPositions, FirmPrices are used
            game.round.data.register_firm_choices(u=u, t=t, position=position, price=price)

            game.round.bots.consumer.play(rd=rd, t=t)
            game.round.state.end_of_turn(rd=rd, rs=rs, t=t)

        return t,  # ! Must be a tuple

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


def ask_firm_active_consumer_choices(u, opp, rm, rd, rs, t):

    if t <= rd.t:

        is_end = int(game.round.state.is_end_of_round(rd=rd, t=t))

        if rs.firm_active_played:

            consumer_choices = game.round.data.get_consumer_choices(rd=rd, t=t)
            consumer_choices = [1 if i == u.firm_id else 0 if i != -1 else -1 for i in consumer_choices]

            if is_end:
                game.round.state.go_to_next_round(u=u, opp=opp, rm=rm)

            return (t,) + tuple((i for i in consumer_choices)) + (is_end,)

        else:
            utils.log("Have to wait: Active firm needs to play", f=utils.fname(), path=__path__)
            return parameters.error["wait"],  # Tuple is necessary!!

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!
