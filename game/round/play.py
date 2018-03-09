# from utils import utils
from parameters import parameters

from game.models import RoundComposition

import game.round.bots.firm
import game.round.bots.consumer
import game.round.state
import game.round.data
import game.room.state

"""
    Here are grouped the functions called by client during the playing phase
"""


# ----------------------------------- init ------------------------------------------------------ #

def ask_firm_init(u, opp, rd_opp, rm, rd, rs):

    #
    if u.state == game.room.state.tutorial:
        game.round.state.go_to_next_round(u=u, opp=opp, rm=rm)
        u.tutorial_progression = 100
        u.save(update_fields=["tutorial_progression"])

    # Maybe client has to wait the other player
    if game.round.state.client_has_to_wait_over_player(u=u, opp=opp, rm=rm):

        if not rm.trial:
            opp_progression = game.round.state.get_opponent_progression(u=u, opp=opp, rd_opp=rd_opp)
            return parameters.error["wait"], opp_progression  # Tuple is necessary!! '-1' hold for wait

    # Get information necessary for firm initialization
    firm_state = "active" if rs.firm_active == u.firm_id else "passive"
    if rd.t == 0:
        positions, prices = game.round.data.get_positions_and_prices(rd=rd, t=rd.t)
    else:
        positions, prices = game.round.data.get_positions_and_prices(rd=rd, t=rd.t - 1)

    profits = game.round.data.get_profits(rd=rd, t=rd.t)

    opp_id = (u.firm_id + 1) % 2

    return \
        rd.t, firm_state, positions[u.firm_id], prices[u.firm_id], profits[u.firm_id], \
        positions[opp_id], prices[opp_id], profits[opp_id], rd.ending_t


# ----------------------------------| passive firm demands |-------------------------------------- #

def ask_firm_passive_opponent_choice(u, rd, rs, opp, rm, t):

    if t <= rd.t:

        # Make bot firm play if applicable
        if not rs.firm_active_and_consumers_played:

            # Get firm bot if there is one
            firm_bot = RoundComposition.objects.filter(round_id=rd.id, bot=True).first()
            # utils.log("There is a bot: {}".format(firm_bot is not None), f=ask_firm_passive_opponent_choice)

            if firm_bot and firm_bot.firm_id == rs.firm_active:

                game.round.bots.firm.play(firm_bot=firm_bot, rd=rd, t=t)
                game.round.bots.consumer.play(rd=rd, t=t)
                game.round.state.end_of_turn(rd=rd, rs=rs, t=t)

        if rs.firm_active_and_consumers_played:

            opponent_id = (u.firm_id + 1) % parameters.n_firms
            positions, prices = game.round.data.get_positions_and_prices(rd=rd, t=t)

            consumer_choices = game.round.data.get_consumer_choices(rd=rd, t=t)
            consumer_choices = [1 if i == u.firm_id else 0 if i != -1 else -1 for i in consumer_choices]

            round_ends = game.round.state.is_end_of_round(rd=rd, t=t)

            if round_ends:
                # utils.log("Round ends", f=ask_firm_passive_opponent_choice)
                game.round.state.go_to_next_round(u=u, opp=opp, rm=rm)

            return (t, positions[opponent_id], prices[opponent_id], ) + \
                    tuple((i for i in consumer_choices)) + (int(round_ends),)

        else:
            # utils.log("Have to wait: Active firm needs to play", f=ask_firm_passive_opponent_choice)
            return parameters.error["wait"],  # Tuple is necessary!!

    else:
        # utils.log("Error: Time is superior!!!!", f=ask_firm_passive_opponent_choice, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


# def ask_firm_passive_consumer_choices(u, opp, rm, rd, rs, t):
#
#     if t <= rd.t:
#
#         if rs.firm_active_and_consumers_played:
#
#
#             return (t,) +
#
#         else:
#             # utils.log("Have to wait: Active firm needs to play", f=ask_firm_passive_consumer_choices)
#             return parameters.error["wait"],  # Tuple is necessary!! // Have to wait
#
#     else:
#         # utils.log("Error: Time is superior!!!!", f=ask_firm_passive_consumer_choices, level=3)
#         return parameters.error["time_is_superior"],  # Time is superior!


# -----------------------------------| active firm demands |-------------------------------------- #

def ask_firm_active_choice_recording(u, rd, rs, opp, rm, t, position, price):

    if t <= rd.t:

        if not rs.firm_active_and_consumers_played:
            # tables FirmPositions, FirmPrices are used
            game.round.data.register_firm_choices(u=u, t=t, position=position, price=price)
            game.round.bots.consumer.play(rd=rd, t=t)
            game.round.state.end_of_turn(rd=rd, rs=rs, t=t)

        if rs.firm_active_and_consumers_played:

            consumer_choices = game.round.data.get_consumer_choices(rd=rd, t=t)
            consumer_choices = [1 if i == u.firm_id else 0 if i != -1 else -1 for i in consumer_choices]

            round_ends = game.round.state.is_end_of_round(rd=rd, t=t)

            if round_ends:
                # utils.log("Round ends", f=ask_firm_active_choice_recording)
                game.round.state.go_to_next_round(u=u, opp=opp, rm=rm)

            return (t,) + tuple((i for i in consumer_choices)) + (int(round_ends),)

    else:
        # utils.log("Error: Time is superior!!!!", f=ask_firm_active_choice_recording, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


# def ask_firm_active_consumer_choices(u, opp, rm, rd, rs, t):
#
#     if t <= rd.t:
#
#         if rs.firm_active_and_consumers_played:
#
#             consumer_choices = game.round.data.get_consumer_choices(rd=rd, t=t)
#             consumer_choices = [1 if i == u.firm_id else 0 if i != -1 else -1 for i in consumer_choices]
#
#             round_ends = game.round.state.is_end_of_round(rd=rd, t=t)
#
#             if round_ends:
#                 # utils.log("Round ends", f=ask_firm_passive_consumer_choices)
#                 game.round.state.go_to_next_round(u=u, opp=opp, rm=rm)
#
#             return (t,) + tuple((i for i in consumer_choices)) + (int(round_ends),)
#
#         else:
#             # utils.log("Have to wait: Active firm needs to play", f=ask_firm_active_consumer_choices)
#             return parameters.error["wait"],  # Tuple is necessary!!
#
#     else:
#         # utils.log("Error: Time is superior!!!!", f=ask_firm_active_consumer_choices, level=3)
#         return parameters.error["time_is_superior"],  # Time is superior!
