import numpy as np
import os

from parameters import parameters
from utils import utils

from game.models import RoundComposition, ConsumerChoice, Round

from game import room, round

__path__ = os.path.relpath(__file__)


# --------------------------------  public  --------------------------- #

def play(rd, t):

    #
    positions, prices = round.dialog.get_positions_and_prices(
        round_id=rd.round_id,
        t=t,
        called_from=__path__ + ':' + utils.fname()
    )

    positions_seen = room.dialog.compute_field_of_view(
        room_id=rd.room_id, to_send=False, called_from=__path__ + "." + utils.fname())

    for agent_id in parameters.n_positions:

        consumer_position = agent_id

        choice = _choice(
            positions=positions, prices=prices, positions_seen=positions_seen[consumer_position])

        new_entry = ConsumerChoice(
            round_id=rd.round_id,
            agent_id=agent_id,
            t=t,
            value=choice
        )
        new_entry.save()


# --------------------------------  protected --------------------------- #

def _choice(positions, prices, positions_seen):

    firms_seen = \
        [i for i, pos in enumerate(positions) if positions_seen[pos]]

    if len(firms_seen) > 1:

        min_price = np.min(prices)
        cheapest = [i for i in firms_seen if prices[i] == min_price]
        return np.random.choice(cheapest)

    elif len(firms_seen) == 1:
        return firms_seen[0]

    else:
        return -1