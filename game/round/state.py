import os
import numpy as np

from parameters import parameters

from game.models import RoundState, RoundComposition

from . import bots, data

from utils import utils


__path__ = os.path.relpath(__file__)


def check_if_bot_firm_has_to_play(rd, rs, t):

    # Log
    utils.log("Called", f=utils.fname(), path=__path__)

    # Check if round contains bots
    if rd.real_players < parameters.n_firms:

        # Get firm bot
        firm_bot = RoundComposition.objects.filter(round_id=rd.round_id, bot=1, role="firm").first()

        # If active firm did not play and bot firms not already played
        if firm_bot.agent_id == rs.firm_active \
                and not rs.firm_active_played:

            position, price = bots.firm.play(rd=rd, t=t)

            data.register_firm_choices(rd=rd, agent=firm_bot,
                                       t=t, position=position, price=price)

            utils.log("Bot firm played.",
                      f=utils.fname(), path=__path__)

            return True

        else:
            utils.log("Bot firm has already played (or is not active).",
                      f=utils.fname(), path=__path__)

    else:
        utils.log("Round does not contain bots.", f=utils.fname(), path=__path__)

    return False


# def check_if_consumers_have_to_play(round_id, t):
#
#     # Log
#     utils.log("Called", f=utils.fname(), path=__path__)
#
#     # Get room state
#     round_state = RoundState.objects.get(round_id=round_id, t=t)
#
#     # Then consumers need to choose a perimeter as well as a firm to buy from
#     if round_state.firm_active_played and not round_state.consumers_played:
#
#         bots.consumer.play(round_id=round_id, t=t)
#
#         round_state.consumers_played = 1
#         round_state.save()
#
#         data.compute_scores(round_id=round_id, t=t)
#         _advance_of_one_time_step(round_id=round_id, t=t)
#         return True
#
#     else:
#         return False

def validate_firm_choice_and_make_consumers_play(rd, rs, t):

    # table RoundComposition, ConsumerChoices are used
    bots.consumer.play(rd, t=t)

    rs.firm_active_played = 1
    rs.consumers_played = 1
    rs.save()

    data.compute_scores(round_id=rd.round_id, t=t)
    _advance_of_one_time_step(rd=rd, t=t)
    # rs.save()


# def init(round_id, ending_t):
#
#     # Random turn by turn
#     first_to_play = np.random.choice(range(parameters.n_firms))
#     firm_states = np.zeros(ending_t)
#     firm_states[first_to_play:ending_t:2] = 1
#
#     for t in range(ending_t):
#
#         round_state = RoundState(
#             round_id=round_id, firm_active=firm_states[t], t=t,
#             firm_active_played=0, consumers_played=0
#         )
#
#         round_state.save()


def delete(rd):

    rs = RoundState.objects.filter(rd=rd)
    if rs:
        rs.delete()


def _advance_of_one_time_step(rd, t):

    if not is_end_of_game(rd, t=t):

        # Increment time state
        rd.t += 1
        rd.save()


def is_end_of_game(rd, t):
    return t == rd.ending_t - 1  # -1 because starts at 0
