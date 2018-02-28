from django.utils import timezone

import os
import subprocess
import pickle
import numpy as np

from utils import utils
from parameters import parameters

from game.models import FirmPosition, FirmPrice, FirmProfit, FirmProfitPerTurn, \
    ConsumerChoice, Round, RoundState, RoundComposition, User, Room


__path__ = os.path.relpath(__file__)


# def init(round_id):
#
#     for firm_id in range(parameters.n_firms):
#
#         for (table, value) in zip(
#                 (FirmProfit, FirmPrice, FirmPosition),
#                 (0,
#                  np.random.randint(1, parameters.n_prices + 1),
#                  np.random.randint(parameters.n_positions))
#         ):
#             entry = table(round_id=round_id, agent_id=firm_id, t=0, value=value)
#             entry.save()


def delete(round_id):

    utils.log("Delete data corresponding to 'round_id' '{}'".format(round_id),
              path=__path__, f=utils.fname())

    for table in \
            (FirmPosition, FirmPrice, FirmProfit, FirmProfitPerTurn, ConsumerChoice):
        entry = table.objects.filter(round_id=round_id)
        if entry.count():
            entry.delete()


def get_init_info(u, rd, rs):

    opponent_id = (u.firm_id + 1) % parameters.n_firms

    d = {i: {"position": 0, "price": 0, "profits": 0} for i in ("opp", "player")}
    d["firm_state"] = "active" if rs.firm_active == u.firm_id else "passive"

    tables = {"position": FirmPosition, "price": FirmPrice, "profits": FirmProfit}
    ids = {"opp": opponent_id, "player": u.agent_id}

    for i in ids.keys():

        for key in d[i].keys():

            entry = tables[key].objects.filter(
                round_id=rd.round_id,
                agent_id=ids[i],
                t=rd.t
            ).first()

            if entry is None:
                entry = tables[key].objects.get(
                    round_id=rd.round_id,
                    agent_id=ids[i],
                    t=rd.t - 1,
                )

            d[i][key] = entry.value

    return d


def get_positions_and_prices(rd, t):

    positions = []
    prices = []

    for firm_id in range(parameters.n_firms):

        position = FirmPosition.objects.get(round_id=rd.round_id, agent_id=firm_id, t=t)
        positions.append(position.value)

        price = FirmPrice.objects.get(round_id=rd.round_id, agent_id=firm_id, t=t)
        prices.append(price.value)

    return positions, prices


def get_consumer_choices(rd, t):

    entries = ConsumerChoice.objects.filter(t=t, round_id=rd.round_id).order_by("agent_id")
    consumer_choices = [i.value for i in entries]
    return consumer_choices


def register_firm_choices(rd, u, t, position, price):

    for i in (t, t + 1):

        for (table, value) in zip(
                (FirmPosition, FirmPrice),
                (position, price)
        ):

            entry = table.objects.filter(round_id=rd.round_id, agent_id=u.firm_id, t=i).first()

            if entry is not None:
                entry.value = value
                entry.save()

            else:
                entry = table(round_id=rd.round_id, agent_id=u.firm_id, t=i, value=value)
                entry.save()

    # rs = RoundState.objects.get(round_id=round_id, t=t)
    # rs.firm_active_played = 1
    # rs.save()


def register_consumer_choices(rd, consumer_choices, t):

    for agent_id, consumer_choice in enumerate(consumer_choices):
        new_entry = ConsumerChoice(round_id=rd.id, agent_id=agent_id, t=t, value=consumer_choice)
        new_entry.save()


def compute_scores(rd, t):

    """
    Deals with tables FirmProfit, FirmPrice, FirmProfitPerTurn
    """

    for firm_id in range(parameters.n_firms):

        sc = FirmProfit.objects.get(round_id=rd.id, agent_id=firm_id, t=t).value

        a_consumer_choices = np.asarray(
                    get_consumer_choices(round_id=rd.id, t=t)
                )

        n_clients = \
            np.sum(a_consumer_choices == firm_id)

        price = FirmPrice.objects.get(round_id=rd.id, agent_id=firm_id, t=t).value

        new_sc_value = sc + n_clients * price
        new_profits_per_turn_value = n_clients * price

        new_profits_per_turn_entry = FirmProfitPerTurn(
            round_id=rd.id,
            agent_id=firm_id,
            t=t+1,
            value=new_profits_per_turn_value
        )

        new_profits_per_turn_entry.save()

        new_sc_entry = FirmProfit(
            round_id=rd.id,
            agent_id=firm_id,
            t=t+1,
            value=new_sc_value
        )
        new_sc_entry.save()


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
            FirmProfitPerTurn,
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
