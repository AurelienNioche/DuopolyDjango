import numpy as np

from parameters import parameters


def compute(radius, to_send=False):
    """

    :param radius:
    :param to_send: if the output is intended to send it to the client, format it as needed
    :return: positions seen by a consumer
    """

    int_radius = round(parameters.n_positions * radius)
    positions = np.arange(parameters.n_positions)

    positions_for_each_consumer = np.zeros((parameters.n_consumers, parameters.n_positions), dtype=int)

    for c in range(parameters.n_consumers):

        cond0 = c - int_radius <= positions
        cond1 = c + int_radius >= positions

        positions_for_each_consumer[c, :] = cond0 * cond1

        # Below, the segment (the beach), with c the position of the consumer under consideration
        # c-int_radius             c        p                        c+int_radius
        # -----|-------------------|--------|----------------------------|----------
        # if p <= pos-int_radius and p >= pos+int_radius then p is seen

    return format_positions(positions_for_each_consumer) if to_send else positions_for_each_consumer


def format_positions(positions_for_each_consumer):
    return "$".join("!".join(str(int(j)) for j in pos) for pos in positions_for_each_consumer)
