import os

from game.models import RoundComposition

from . import data
from . bots import firm, consumer

from utils import utils


__path__ = os.path.relpath(__file__)


def check_if_bot_firm_has_to_play(rd, rs, t):

    # Log
    utils.log("Called", f=utils.fname(), path=__path__)

    # Get firm bot
    firm_bot = RoundComposition.objects.filter(round_id=rd.id, bot=True).first()

    # Check if round contains bots
    if firm_bot:

        # If active firm did not play and bot firms not already played
        if firm_bot.firm_id == rs.firm_active and not rs.firm_active_played:

            position, price = firm.play(firm_bot=firm_bot, rd=rd, t=t)

            data.register_firm_choices(u=firm_bot, t=t, position=position, price=price)

            utils.log("Bot firm played.",
                      f=utils.fname(), path=__path__)

            return True

        else:
            utils.log("Bot firm has already played (or is not active).",
                      f=utils.fname(), path=__path__)
            return False
    else:
        utils.log("Round does not contain bots.", f=utils.fname(), path=__path__)

    return False


def validate_firm_choice_and_make_consumers_play(rd, rs, t):

    # table RoundComposition, ConsumerChoices are used
    consumer.play(rd=rd, t=t)

    rs.firm_active_played = True
    rs.consumers_played = True
    rs.save(update_fields=("firm_active_played", "consumers_played", ))

    data.compute_scores(rd=rd, t=t)
    _advance_of_one_time_step(rd=rd, t=t)
    # rs.save()


def _advance_of_one_time_step(rd, t):

    if not is_end_of_game(rd=rd, t=t):

        # Increment time state
        rd.t += 1
        rd.save()


def is_end_of_game(rd, t):
    return t == rd.ending_t - 1  # -1 because starts at 0
