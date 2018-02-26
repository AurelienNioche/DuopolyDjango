from django.http import HttpResponse
from django.db import transaction
from django.db.utils import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import os

from utils import utils

from . import tutorial, room, round, player

__path__ = os.path.relpath(__file__)


@csrf_exempt
def client_request(request):

    """
    main method taking request from client
    and returning
    :param request:
    :return: response
    """

    utils.log("Post request: {}".format(list(request.POST.items())),
              f=utils.fname(), path=__path__)

    demand = request.POST["demand"]

    try:
        # Retrieve functions declared in the current script
        functions = {f_name: f for f_name, f in globals().items() if not f_name.startswith("_")}
        # Retrieve demanded function
        func = functions[demand]
    except KeyError:
        raise Exception("Bad demand")

    to_reply = "/".join((str(i) for i in func(request)))

    utils.log("I will reply '{}' to client.".format(to_reply), f=utils.fname(), path=__path__)
    response = HttpResponse(to_reply)
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Headers"] = "Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Origin"] = "*"

    return response


# ----------------------| Demands relative to registration |--------------------------------------------------------- #


def register(request):

    user_mail = request.POST["email"].lower()
    nationality = request.POST["nationality"]
    gender = request.POST["gender"]
    age = request.POST["age"]
    mechanical_id = request.POST["mechanical_id"]

    went_well = room.client.register_as_user(
        user_mail=user_mail,
        nationality=nationality,
        gender=gender,
        age=age,
        mechanical_id=mechanical_id
    )

    if went_well:
        return "reply", utils.fname(), 1

    else:
        return "reply", utils.fname(), 0, "sending_aborted"


def send_password_again(request):

    """
    Get called when user wants to renew its password
    :param request:
    :return: 1 if it worked, 0 else
    """

    user_mail = request.POST["email"].lower()
    nationality = request.POST["nationality"],
    gender = request.POST["gender"],
    age = request.POST["age"],
    mechanical_id = request.POST["mechanical_id"]

    went_well = room.client.send_password_again(
        user_mail=user_mail,
        nationality=nationality,
        gender=gender,
        age=age,
        mechanical_id=mechanical_id
    )

    return "reply", utils.fname(), int(went_well)

# ----------------------------------| Participation |--------------------------------------------------------------- #


@player.management.connection_checker
def connect(request):

    username = request.POST["username"].lower()
    password = request.POST["password"]

    went_well = room.client.connect(username=username, password=password)
    return "reply", utils.fname(), int(went_well)


@player.management.connection_checker
def registered_as_player(request):

    username = request.POST["username"].lower()
    rsp = room.client.registered_as_player(username)

    if rsp:
        return ("reply", utils.fname(), 1) + rsp

    else:
        return "reply", utils.fname(), 0


@player.management.connection_checker
def room_available(request):

    username = request.POST["username"].lower()
    utils.log("{} asks for a room available.".format(username), f=utils.fname(), path=__path__)

    # 1 if a room is available, else 0
    rsp = room.client.room_available()

    return "reply", utils.fname(), rsp


@player.management.connection_checker
def proceed_to_registration_as_player(request):

    username = request.POST["username"].lower()

    with transaction.atomic():

        # try:
        rsp = room.client.proceed_to_registration_as_player(username=username)

        # except IntegrityError:
        #     transaction.rollback()
        #     return "reply", "error", "player_is_not_unique"

    if rsp:
        return ("reply", utils.fname(), 1) + rsp

    else:
        return "reply", utils.fname(), 0


# ----------------------------------| Demand relatives to Tutorial  |------------------------------------------------- #

@player.management.connection_checker
def tutorial_done(request):

    player_id = request.POST["player_id"]
    tutorial.client.tutorial_done(player_id=player_id)
    return "reply", utils.fname()


@player.management.connection_checker
def submit_tutorial_progression(request):

    player_id = request.POST["player_id"]
    tutorial_progression = float(request.POST["tutorial_progression"].replace(",", "."))
    tutorial.client.record_tutorial_progression(player_id=player_id, tutorial_progression=tutorial_progression)
    return "reply", utils.fname()


# ------------------------| Players ask for missing players in their before starting to playing  |------------------- #

# @transaction.atomic
@player.management.connection_checker
def missing_players(request):

    player_id = request.POST["player_id"]
    n = room.client.missing_players(player_id=player_id)
    return "reply", utils.fname(), n


# ------------------------| Firms ask for their init info at the beginning of each round |-------------------------- #

@player.management.connection_checker
def ask_firm_init(request):

    player_id = request.POST["player_id"]

    to_reply = round.client.ask_firm_init(
        player_id=player_id
    )

    return ("reply", utils.fname(), ) + to_reply

# ----------------------------------| passive firm demands |----------------------------------------------------- #


@player.management.connection_checker
def ask_firm_passive_opponent_choice(request):

    """
    called by a passive firm
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])

    to_reply = round.client.ask_firm_passive_opponent_choice(
        player_id=player_id,
        t=t
    )

    return ("reply", utils.fname(), ) + to_reply


@player.management.connection_checker
def ask_firm_passive_consumer_choices(request):

    """
    Called by a passive firm in order to get consumers' firm choices.
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])

    to_reply = round.client.ask_firm_passive_consumer_choices(
        player_id=player_id,
        t=t
    )

    return ("reply", utils.fname(), ) + to_reply

# -----------------------------------| active firm demands |-------------------------------------------------------- #


@player.management.connection_checker
def ask_firm_active_choice_recording(request):
    """
    called by active firm
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])
    position = int(request.POST["position"])
    price = int(request.POST["price"])

    to_reply = round.client.ask_firm_active_choice_recording(
        player_id=player_id,
        t=t,
        position=position,
        price=price
    )

    return ("reply", utils.fname(), ) + to_reply


@player.management.connection_checker
def ask_firm_active_consumer_choices(request):

    """
    called by active firm
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])

    to_reply = round.client.ask_firm_active_consumer_choices(
        player_id=player_id,
        t=t
    )

    return ("reply", utils.fname(), ) + to_reply
