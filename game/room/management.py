import os
import numpy as np

from utils import utils
from parameters import parameters

from game.models import Room, User, Round, RoundComposition, RoundState, FirmProfit, FirmPrice, FirmPosition


from game import round

from . import state

__path__ = os.path.relpath(__file__)


def create(data):

    """
    Called by dashboard
    :param data:
    :return:
    """

    trial = int(bool(data['trial']))
    ending_t = int(data["ending_t"])
    radius = data['radius']
    nb_of_room = int(data["nb_of_room"])

    missing_players = 1 if trial else 2

    for r in range(nb_of_room):

        rm = Room(
            state=state.tutorial,
            ending_t=ending_t,
            radius=radius,
            user_id_0=-1,
            user_id_1=-1,
            trial=trial,
            missing_players=missing_players,
            opened=True
        )

        rm.save()

        print("room_id", rm.id)

        # Create rounds and their composition ------------------------------ #

        class Pvp:
            real_players = missing_players
            name = "pvp"

        class Pve:
            real_players = 1
            name = "pve"

        # noinspection PyTypeChecker
        round_types = (Pve,) * 2 + (Pvp,)

        for rt in round_types:

            # Create round --------------------------- #

            rd = Round(
                room_id=rm.id,
                real_players=rt.real_players,
                missing_players=rt.real_players,
                ending_t=ending_t,
                state=rt.name,
                t=0,
            )

            rd.save()  # Have to save before access to id

            # Create composition ----------------------------#
            bots = np.ones(parameters.n_firms)

            bots[:rd.real_players] = 0

            for i in range(parameters.n_firms):
                composition = RoundComposition(
                    round_id=rd.id,
                    user_id=-1,
                    firm_id=i,
                    bot=bool(bots[i])
                )

                composition.save()

            # Create data --------------------------------- #

            for firm_id in range(parameters.n_firms):

                for (table, value) in zip(
                        (FirmProfit, FirmPrice, FirmPosition),
                        (0,
                         np.random.randint(1, parameters.n_prices + 1),
                         np.random.randint(parameters.n_positions))
                ):
                    entry = table(round_id=rd.id, agent_id=firm_id, t=0, value=value)
                    entry.save()

            # Create state ---------------------------------- #

            # Random turn by turn
            first_to_play = np.random.choice(range(parameters.n_firms))
            firm_states = np.zeros(ending_t)
            firm_states[first_to_play:ending_t:2] = 1

            for t in range(ending_t):
                round_state = RoundState(
                    round_id=rd.id, firm_active=firm_states[t], t=t,
                    firm_active_played=0, consumers_played=0
                )

                round_state.save()


# def delete(rm, rounds):
#
#     """
#     Get room and compositions related then delete
#     """
#
#     if rm:
#         rm.delete()
#
#     # entries = Players.objects.filter(room_id=rm.room_id)
#     # if entries:
#     #     entries.delete()
#
#     entries = Round.objects.filter(room_id=rm.room_id)
#
#     for rd in entries:
#
#         composition.delete(rd=rd)
#         state.delete(rd=rd)
#         data.delete(rd=rd)
#
#         rd.delete()


def close(rm):

    rm.opened = 0
    rm.save()
    utils.log("The room {} is now closed.".format(rm.room_id), f=utils.fname(), path=__path__)


def get_list(rooms):

    class ConnectedPlayer:
        def __init__(self, username, connected, deserter, p_state, last_request, time_last_request):
            self.username = username
            self.deserter = deserter
            self.connected = connected
            self.state = p_state
            self.last_request = last_request
            self.time_last_request = time_last_request

    rooms = rooms.order_by("id")
    rooms_list = []

    for room in rooms:

        users = User.objects.filter(registered=True)
        connected_players = []

        for u in users:

            cp = ConnectedPlayer(
                username=u.username,
                connected=u.connected,
                deserter=u.deserter,
                p_state=u.state,
                last_request=u.last_request,
                time_last_request=u.time_last_request
            )

            connected_players.append(cp)

        dic = {"att": room, "connected_players": connected_players}
        rooms_list.append(dic)

    return rooms_list


