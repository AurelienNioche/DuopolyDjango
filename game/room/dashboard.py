import numpy as np

from game.models import Room, Round, RoundState, RoundComposition, FirmPosition, FirmPrice, FirmProfit, \
    FirmProfitPerTurn, ConsumerChoice, User

from parameters import parameters

from . import state


def delete(room_id):

    rm = Room.objects.filter(id=room_id).first()
    rds = Round.objects.filter(room_id=rm.id)

    for rd in rds:

        if rd:
            rs = RoundState.objects.filter(round_id=rd.id)
            rc = RoundComposition.objects.filter(round_id=rd.id)
            fpr = FirmProfit.objects.filter(round_id=rd.id)
            fpr_t = FirmProfitPerTurn.objects.filter(round_id=rd.id)
            fpc = FirmPrice.objects.filter(round_id=rd.id)
            fp = FirmPosition.objects.filter(round_id=rd.id)
            cc = ConsumerChoice.objects.filter(round_id=rd.id)

            for i in (rs, rc, fpr, fpr_t, fpc, fp, cc):
                if i.exists():
                    i.delete()

            rd.delete()

    if rm:
        rm.delete()


def create(data):

    Room.objects.select_for_update().all()

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


def get_list():

    rooms = Room.objects.all()
    users = User.objects.filter(registered=True)

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
