import os
import numpy as np

from parameters import parameters

from game.models import RoundState, Round


__path__ = os.path.relpath(__file__)


def init(round_id, ending_t):

    # Random turn by turn
    first_to_play = np.random.choice(range(parameters.n_firms))
    firm_states = np.zeros(ending_t)
    firm_states[first_to_play:ending_t:2] = 1

    for t in range(ending_t):

        round_state = RoundState(
            round_id=round_id, firm_active=firm_states[t], t=t,
            firm_active_played=0, consumers_played=0
        )

        round_state.save()


def delete(round_id):

    rs = RoundState.objects.filter(round_id=round_id)
    if rs:
        rs.delete()


def advance_of_one_time_step(round_id, t):

    # Get the round object
    rd = Round.objects.get(round_id=round_id)

    if not is_end_of_game(round_id=round_id, t=t):

        # Increment time state
        rd.t += 1
        rd.save(force_update=True)


def is_end_of_game(round_id, t):

    rd = Round.objects.get(round_id=round_id)
    return t == rd.ending_t - 1  # -1 because starts at 0

