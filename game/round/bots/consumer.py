import numpy as np
import os

from parameters import parameters

from game.models import ConsumerChoice

import game.round.data
import game.room.field_of_view

__path__ = os.path.relpath(__file__)


# --------------------------------  public  --------------------------- #

def play(rd, t):

    positions, prices = game.round.data.get_positions_and_prices(rd=rd, t=t)

    positions_seen = game.room.field_of_view.compute(radius=rd.radius, to_send=False)

    for agent_id in range(parameters.n_positions):

        choice = _choice(
            positions=positions, prices=prices, positions_seen=positions_seen[agent_id])

        # Save choice
        e = ConsumerChoice.objects.get(round_id=rd.id, agent_id=agent_id, t=t)
        e.value = choice
        e.save(update_fields=("value",))


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
