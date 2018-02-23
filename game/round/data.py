from django.utils import timezone

import os
import subprocess
import pickle
import numpy as np

from utils import utils
from parameters import parameters

from game.models import FirmPositions, FirmPrices, FirmProfits, FirmProfitsPerTurn, \
    ConsumerChoices, Players, Round, RoundState, RoundComposition, Users, Room


__path__ = os.path.relpath(__file__)


def init(round_id):

    for agent_id in range(parameters.n_firms):

        for (table, value) in zip(
                (FirmProfits, FirmPrices, FirmPositions),
                (0,
                 np.random.randint(1, parameters.n_prices + 1),
                 np.random.randint(parameters.n_positions))
        ):
            entry = table(round_id=round_id, agent_id=agent_id, t=0, value=value)
            entry.save()


def delete(round_id):

    utils.log("Delete data corresponding to 'round_id' '{}'".format(round_id),
              path=__path__, f=utils.fname())

    for table in \
            (FirmPositions, FirmPrices, FirmProfits, FirmProfitsPerTurn, ConsumerChoices):
        entry = table.objects.filter(round_id=round_id)
        if entry.count():
            entry.delete()


def get_init_info(player_id):

    p = Players.objects.get(player_id=player_id)
    rd = Round.objects.get(round_id=p.round_id)
    rs = RoundState.objects.get(round_id=rd.round_id, t=rd.t)

    agent_id = RoundComposition.objects.get(round_id=rd.round_id, player_id=player_id).agent_id

    opponent_id = (agent_id + 1) % parameters.n_firms

    d = {i: {"position": 0, "price": 0, "profits": 0} for i in ("opp", "player")}
    d["firm_state"] = "active" if rs.firm_active == agent_id else "passive"

    tables = {"position": FirmPositions, "price": FirmPrices, "profits": FirmProfits}
    ids = {"opp": opponent_id, "player": agent_id}

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


def get_positions_and_prices(round_id, t):

    positions = []
    prices = []

    for agent_id in range(parameters.n_firms):

        position = FirmPositions.objects.get(round_id=round_id, agent_id=agent_id, t=t)
        positions.append(position.value)

        price = FirmPrices.objects.get(round_id=round_id, agent_id=agent_id, t=t)
        prices.append(price.value)

    return positions, prices


def get_consumer_choices(round_id, t):

    entries = ConsumerChoices.objects.filter(t=t, round_id=round_id).order_by("agent_id")
    consumer_choices = [i.value for i in entries]
    return consumer_choices


def register_firm_choices(round_id, agent_id, t, position, price):

    for i in (t, t + 1):

        for (table, value) in zip(
                (FirmPositions, FirmPrices),
                (position, price)
        ):

            entry = table.objects.filter(round_id=round_id, agent_id=agent_id, t=i).first()

            if entry is not None:
                entry.value = value
                entry.save(force_update=True)

            else:
                entry = table(round_id=round_id, agent_id=agent_id, t=i, value=value)
                entry.save()

    rs = RoundState.objects.get(round_id=round_id, t=t)
    rs.firm_active_played = 1
    rs.save(force_update=True)


def register_consumer_choices(round_id, agent_id, t, firm_choice):

    new_entry = ConsumerChoices(round_id=round_id, agent_id=agent_id, t=t, value=firm_choice)
    new_entry.save()


def compute_scores(round_id, t):

    for agent_id in range(parameters.n_firms):

        sc = FirmProfits.objects.get(round_id=round_id, agent_id=agent_id, t=t).value

        a_consumer_choices = np.asarray(
                    get_consumer_choices(round_id=round_id, t=t)
                )

        n_clients = \
            np.sum(a_consumer_choices == agent_id)

        price = FirmPrices.objects.get(round_id=round_id, agent_id=agent_id, t=t).value

        new_sc_value = sc + n_clients * price
        new_profits_per_turn_value = n_clients * price

        new_profits_per_turn_entry = FirmProfitsPerTurn(
            round_id=round_id,
            agent_id=agent_id,
            t=t+1,
            value=new_profits_per_turn_value
        )

        new_profits_per_turn_entry.save()

        new_sc_entry = FirmProfits(
            round_id=round_id,
            agent_id=agent_id,
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
            Players,
            Users,
            Room,
            Round,
            RoundComposition,
            RoundState,
            FirmProfits,
            FirmPositions,
            FirmPrices,
            FirmProfits,
            FirmProfitsPerTurn,
            ConsumerChoices
    ):
        # Convert all entries to valid pure python
        attr = list(vars(i) for i in table.objects.all())
        valid_attr = [{k: v for k, v in i.items() if type(v) in (bool, int, str, float)} for i in attr]

        d[table.__name__] = valid_attr

    pickle.dump(file=open(mydata.file_path, "wb"), obj=d)

    return mydata.to_return


def convert_data_to_sql():

    mydata = get_path("sql")

    subprocess.call(["pg_dump", "-U", "dasein", "DuopolyDB", ">", mydata.file_path])

    return mydata.to_return

