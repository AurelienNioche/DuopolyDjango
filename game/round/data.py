import os
import numpy as np


from parameters import parameters

from game.models import FirmPosition, FirmPrice, FirmProfit, ConsumerChoice


__path__ = os.path.relpath(__file__)


def get_init_info(u, rd, rs):

    opponent_id = (u.firm_id + 1) % parameters.n_firms

    d = {i: {"position": 0, "price": 0, "profits": 0} for i in ("opp", "player")}
    d["firm_state"] = "active" if rs.firm_active == u.firm_id else "passive"

    tables = {"position": FirmPosition, "price": FirmPrice, "profits": FirmProfit}
    ids = {"opp": opponent_id, "player": u.firm_id}

    for i in ids.keys():

        for key in d[i].keys():

            entry = tables[key].objects.filter(
                round_id=rd.id,
                agent_id=ids[i],
                t=rd.t
            ).first()

            d[i][key] = entry.value

    return d


def get_positions_and_prices(rd, t):

    positions = []
    prices = []

    for firm_id in range(parameters.n_firms):

        position = FirmPosition.objects.get(round_id=rd.id, agent_id=firm_id, t=t)
        positions.append(position.value)

        price = FirmPrice.objects.get(round_id=rd.id, agent_id=firm_id, t=t)
        prices.append(price.value)

    return positions, prices


def get_consumer_choices(rd, t):

    entries = ConsumerChoice.objects.filter(t=t, round_id=rd.id).order_by("agent_id")
    consumer_choices = [i.value for i in entries]
    return consumer_choices


def register_firm_choices(u, t, position, price):

    for i in (t, t + 1):

        for (table, value) in zip(
                (FirmPosition, FirmPrice),
                (position, price)
        ):

            entry = table.objects.get(round_id=u.round_id, agent_id=u.firm_id, t=i)
            entry.value = value
            entry.save(update_fields=("value", ))


def compute_scores(rd, t):

    """
    Deals with tables FirmProfit, FirmPrice, FirmProfitPerTurn
    """

    for firm_id in range(parameters.n_firms):

        consumer_choices = \
            np.asarray(get_consumer_choices(rd=rd, t=t))

        n_clients = np.sum(consumer_choices == firm_id)

        price = FirmPrice.objects.get(round_id=rd.id, agent_id=firm_id, t=t).value

        e = FirmProfit.objects.get(round_id=rd.id, agent_id=firm_id, t=t)
        sc = e.value

        new_sc = sc + n_clients * price

        e = FirmProfit.objects.get(round_id=rd.id, agent_id=firm_id, t=t+1)
        e.value = new_sc
        e.save(update_fields=("value", ))
