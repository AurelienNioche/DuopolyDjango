import numpy as np
from django_bulk_update.helper import bulk_update

from utils import utils

from game.models import ConsumerChoice

import game.round.data
import game.round.field_of_view


def play(rd, t):

    utils.log("Make play customers", f=play)

    positions, prices = game.round.data.get_positions_and_prices(rd=rd, t=t)

    positions_seen = game.round.field_of_view.compute(radius=rd.radius, to_send=False)

    consumers = ConsumerChoice.objects.filter(round_id=rd.id, t=t).order_by("agent_id")

    for agent_id, c in enumerate(consumers):

        choice = _choice(
            positions=positions, prices=prices, positions_seen=positions_seen[agent_id])

        # Save choice
        c.value = choice

    bulk_update(consumers, update_fields=['value'])


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
