from django.utils import timezone

import os
import subprocess
import pickle

from game.models import FirmPosition, FirmPrice, FirmProfit, \
    ConsumerChoice, Round, RoundState, RoundComposition, User, Room


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


