import numpy as np
from django.utils import timezone

import os
import subprocess
import pickle

from game.models import Room, Round, RoundState, RoundComposition, FirmPosition, FirmPrice, FirmProfit, \
    ConsumerChoice, User, RoomComposition

from parameters import parameters

from . import state


def delete(room_id):

    rm = Room.objects.filter(id=room_id).first()
    rmc = RoomComposition.objects.filter(room_id=room_id)
    if rmc:
        rmc.delete()
    rds = Round.objects.filter(room_id=rm.id)

    for rd in rds:

        if rd:
            rs = RoundState.objects.filter(round_id=rd.id)
            rc = RoundComposition.objects.filter(round_id=rd.id)
            fpr = FirmProfit.objects.filter(round_id=rd.id)
            fpc = FirmPrice.objects.filter(round_id=rd.id)
            fp = FirmPosition.objects.filter(round_id=rd.id)
            cc = ConsumerChoice.objects.filter(round_id=rd.id)

            for i in (rs, rc, fpr, fpc, fp, cc):
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

    # We do bulk creates to limit the nb of hits
    rooms = Room.objects.bulk_create([
        Room(
            state=state.tutorial,
            ending_t=ending_t,
            radius=radius,
            trial=trial,
            missing_players=missing_players,
            opened=True
        ) for _ in range(nb_of_room)
    ])

    RoomComposition.objects.bulk_create([
          RoomComposition(room_id=rm.id) for rm in rooms
    ])

    if not trial:
        RoomComposition.objects.bulk_create([
            RoomComposition(
                room_id=rm.id,
                available=True,
                user_id=-1
            ) for rm in rooms
        ])

    # ---- prepare storage list -------- #
    # These lists contain objects
    # that will be used in a bulk_create
    # in order to limit the nb of hits to the
    # database
    rds = []
    compositions = []
    round_states = []
    firm_profits = []
    firm_prices = []
    firm_positions = []
    consumer_choices = []

    if trial:
        rounds_are_pvp = (False, True)
    else:
        rounds_are_pvp = (False, False, True)

    # fill the lists
    for rm in rooms:

        # Create rounds and their composition ------------------------------ #
        for pvp in rounds_are_pvp:

            there_is_a_bot = int(not pvp or trial)

            rd = Round(
                    room_id=rm.id,
                    missing_players=parameters.n_firms - there_is_a_bot,
                    ending_t=ending_t,
                    pvp=pvp,
                    radius=radius,
                    t=0,
                )

            rd.save(commit=False)

            rds.append(rd)

            for i in range(parameters.n_firms):

                bot = True if i == 0 and there_is_a_bot else False

                compositions.append(
                    RoundComposition(
                        round_id=rd.id,
                        user_id=-1,
                        firm_id=i,
                        bot=bot,
                        available=not bot
                    )
                )

            # Create state ---------------------------------- #

            # Random turn by turn
            first_to_play = np.random.choice(range(parameters.n_firms))
            firm_states = np.zeros(ending_t)
            firm_states[first_to_play:ending_t:2] = 1

            for t in range(ending_t):
                round_states.append(
                    RoundState(
                        round_id=rd.id,
                        firm_active=firm_states[t],
                        t=t,
                        firm_active_and_consumers_played=False
                    )
                )

            # Create data --------------------------------- #

            # Initialize position, price, profit for t = 0
            for firm_id in range(parameters.n_firms):

                price = np.random.randint(1, parameters.n_prices + 1)
                position = np.random.randint(parameters.n_positions)
                profit = 0

                firm_prices.append(FirmPrice(round_id=rd.id, agent_id=firm_id, t=0, value=price))

                firm_positions.append(FirmPosition(round_id=rd.id, agent_id=firm_id, t=0, value=position))

                firm_positions.append(FirmProfit(round_id=rd.id, agent_id=firm_id, t=0, value=profit))

            # Create entries for other t
            for table, lst in zip(
                    (FirmProfit, FirmPrice, FirmPosition),
                    (firm_profits, firm_prices, firm_positions)
            ):

                # Add a supplementary line for avoiding multiple test for knowing when this is the end
                for t in range(1, ending_t + 1):

                    for firm_id in range(parameters.n_firms):

                        lst.append(table(round_id=rd.id, agent_id=firm_id, t=t, value=-1))

            # Create entries for consumer t
            for t in range(0, ending_t):

                for agent_id in range(parameters.n_positions):

                    consumer_choices.append(
                        ConsumerChoice(
                            round_id=rd.id,
                            agent_id=agent_id,
                            t=t,
                            value=-1
                        )
                    )

    # --------------- bulk_create all the lists ----------- #

    Round.objects.bulk_create(rds)
    RoundComposition.objects.bulk_create(compositions)
    RoundState.objects.bulk_create(round_states)
    FirmPrice.objects.bulk_create(firm_prices)
    FirmPosition.objects.bulk_create(firm_positions)
    FirmProfit.objects.bulk_create(firm_profits)
    ConsumerChoice.objects.bulk_create(consumer_choices)


def get_list():

    rooms = Room.objects.all().order_by("id")
    users = User.objects.filter(registered=True)

    rooms_list = []

    for rm in rooms:

        users_room = [i for i in users.filter(room_id=rm.id)]

        dic = {"att": rm, "connected_players": users_room}
        rooms_list.append(dic)

    return rooms_list


def get_path(dtype):

    class Data:
        time_stamp = str(timezone.datetime.now()).replace(" ", "_")
        file_name = "{}_{}_.{}".format(dtype, time_stamp, dtype)
        folder_name = "game_data"
        folder_path = os.getcwd() + "/static/" + folder_name
        file_path = folder_path + "/" + file_name
        to_return = folder_name + "/" + file_name

    os.makedirs(Data.folder_path, exist_ok=True)

    return Data()


def convert_data_to_pickle():

    mydata = get_path("p")

    d = {}

    for table in (
            User,
            Room,
            Round,
            RoundComposition,
            RoundState,
            FirmProfit,
            FirmPosition,
            FirmPrice,
            FirmProfit,
            ConsumerChoice
    ):
        # Convert all entries to valid pure python
        attr = list(vars(i) for i in table.objects.all())
        valid_attr = [{k: v for k, v in i.items() if type(v) in (bool, int, str, float)} for i in attr]

        d[table.__name__] = valid_attr

    pickle.dump(file=open(mydata.file_path, "wb"), obj=d)

    return mydata.to_return


def convert_data_to_sql():

    sql_file = get_path("sql")
    db_name = "duopoly.sqlite3"
    db_path = sql_file.folder_path + "/" + db_name
    to_return = sql_file.folder_name + "/" + db_name

    subprocess.call("pg_dump -U dasein DuopolyDB > {}".format(sql_file.file_path), shell=True)

    subprocess.call("rm {}".format(db_path), shell=True)
    subprocess.call("java -jar pg2sqlite.jar -d {} -o {}".format(sql_file.file_path, db_path), shell=True)

    return to_return
