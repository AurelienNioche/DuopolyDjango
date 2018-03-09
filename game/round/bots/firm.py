import numpy as np
import itertools as it
import pickle
import os

from parameters import parameters
from utils import utils

from game.models import FirmPosition, FirmPrice

import game.round.data


# --------------------------------  global variables ------------------------------- #
options = np.array(list(it.product(range(parameters.n_positions), range(1, parameters.n_prices + 1))))
exp_profits = np.zeros(len(options))

# Folder where we store z (firm decision matrix)
dir_path = os.path.dirname(os.path.realpath(__file__)) + "/data/"


# --------------------------------  high level functions --------------------------- #

def play(firm_bot, rd, t):

    # utils.log("Make bot firm play", f=play)

    opp_id = (firm_bot.firm_id + 1) % parameters.n_firms  # 0 or 1

    opp_position = FirmPosition.objects.get(round_id=rd.id, agent_id=opp_id, t=t).value
    opp_price = FirmPrice.objects.get(round_id=rd.id, agent_id=opp_id, t=t).value
    position, price = _choice(opp_position, opp_price, rd.radius)

    game.round.data.register_firm_choices(u=firm_bot, t=t, position=position, price=price)


# --------------------------------  protected --------------------------- #

def _choice(opp_pos, opp_price, r):

    # ---- get firms' decision matrix --- #
    file_path = dir_path + "/z_{}.p".format(r)

    try:
        z = pickle.load(file=open(file_path, "rb"))

    except FileNotFoundError:

        # If z folder does not exists
        os.makedirs(dir_path, exist_ok=True)

        # Compute firms' decision matrix
        _compute_z(r, file_path)
        z = pickle.load(file=open(file_path, "rb"))

    # ----------------------------------- #

    for i, (pos, price) in enumerate(options):

        n_consumers = z[pos, opp_pos, 0]
        to_share = z[pos, opp_pos, 2]

        if price < opp_price:
            n_consumers += to_share

        elif price == opp_price:
            n_consumers += round(to_share / 2)

        exp_profits[i] = price * n_consumers

    idx = np.flatnonzero(exp_profits == max(exp_profits))
    i = np.random.choice(idx)

    return options[i]


def _compute_z(r, file_path):

    z = np.zeros((parameters.n_positions, parameters.n_positions, 3), dtype=int)
    # Last parameter is idx0: n consumers seeing only A,
    #                   idx1: n consumers seeing only B,
    #                   idx2: consumers seeing A and B,

    r = round(r * parameters.n_positions)

    for i, j in it.product(range(parameters.n_positions), repeat=2):

        for idx in range(parameters.n_consumers):

            field_of_view = (
                max(idx - r, 0),
                min(idx + r, parameters.n_positions)
            )

            see_firm_0 = field_of_view[0] <= i <= field_of_view[1]
            see_firm_1 = field_of_view[0] <= j <= field_of_view[1]

            if see_firm_0 and see_firm_1:
                z[i, j, 2] += 1

            elif see_firm_0:
                z[i, j, 0] += 1

            elif see_firm_1:
                z[i, j, 1] += 1

    pickle.dump(obj=z, file=open(file_path, "wb"))
