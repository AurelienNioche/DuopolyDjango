from django.http import HttpResponse
from django.db import transaction
from django.db.utils import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import os

from utils import utils

from game.models import User, Room, Round, RoundComposition, RoundState

from . import room, round, player

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

    #######################
    # !!!!!!!!!!!!!!!!!!!!!!!!!!
    # BROKEN

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

    u = User.objects.filter(username=user_mail)

    went_well = room.client.send_password_again(
        u=u,
        user_mail=user_mail,
        nationality=nationality,
        gender=gender,
        age=age,
        mechanical_id=mechanical_id
    )

    return "reply", utils.fname(), int(went_well)

# ----------------------------------| Participation |--------------------------------------------------------------- #


def connect(request):

    # Get info from POST
    username = request.POST["username"].lower()
    password = request.POST["password"]

    # Get data from table
    users = User.objects.all()

    # Check connection
    player.client.connection_checker(
        called_from=connect.__name__,
        users=users,
        username=username
    )

    went_well = room.client.connect(users=users, username=username, password=password)
    return "reply", utils.fname(), int(went_well)


def registered_as_player(request):

    # Get info from POST
    username = request.POST["username"].lower()

    # Get data from table
    users = User.objects.all()

    # Check connection
    raise_an_error, type_of_error = player.client.connection_checker(
        called_from=connect.__name__,
        users=users,
        username=username
    )
    if raise_an_error:
        return "reply", utils.fname(), type_of_error

    # Get data from table
    users = User.objects.select_for_update().all()
    rooms = Room.objects.select_for_update().all()
    rounds = Round.objects.select_for_update().all()
    round_compositions = RoundComposition.objects.select_for_update().all()

    rsp = room.client.registered_as_player(users=users, rooms=rooms, rounds=rounds,
                                           round_compositions=round_compositions, username=username)

    if rsp:
        return ("reply", utils.fname(), 1) + rsp

    else:
        return "reply", utils.fname(), 0


def room_available(request):

    username = request.POST["username"].lower()
    utils.log("{} asks for a room available.".format(username), f=utils.fname(), path=__path__)

    # 1 if a room is available, else 0
    rsp = room.client.room_available()

    return "reply", utils.fname(), rsp


def proceed_to_registration_as_player(request):

    username = request.POST["username"].lower()

    with transaction.atomic():
        rsp = room.client.proceed_to_registration_as_player(username=username)

    if rsp:
        return ("reply", utils.fname(), 1) + rsp

    else:
        return "reply", utils.fname(), 0


# ----------------------------------| Demand relatives to Tutorial  |------------------------------------------------- #

def tutorial_done(request):

    player_id = request.POST["player_id"]

    u = User.objects.get(id=player_id)
    rd = Round.objects.get(round_id=u.round_id)
    rm = Room.objects.get(room_id=u.room_id)

    player.client.go_to_next_round(
        p=u,
        rm=rm,
        rd=rd,
        called_from=__path__ + ":" + utils.fname()
    )

    return "reply", utils.fname()


def submit_tutorial_progression(request):

    player_id = request.POST["player_id"]
    tutorial_progression = float(request.POST["tutorial_progression"].replace(",", "."))

    p = User.objects.get(id=player_id)

    p.tutorial_progression = tutorial_progression * 100
    p.save()

    return "reply", utils.fname()


# ------------------------| Players ask for missing players in their before starting to playing  |------------------- #


def missing_players(request):

    player_id = request.POST["player_id"]

    u = User.objects.get(id=player_id)
    rm = Room.objects.get(id=u.room_id)

    return "reply", utils.fname(), rm.missing_players


# ------------------------| Firms ask for their init info at the beginning of each round |-------------------------- #

def ask_firm_init(request):

    player_id = request.POST["player_id"]

    to_reply = round.client.ask_firm_init(
        player_id=player_id
    )

    return ("reply", utils.fname(), ) + to_reply

# ----------------------------------| passive firm demands |----------------------------------------------------- #


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


def ask_firm_passive_consumer_choices(request):

    """
    Called by a passive firm in order to get consumers' firm choices.
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])

    u = User.objects.get(id=player_id)

    rd = Round.objects.get(round_id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    to_reply = round.client.ask_firm_passive_consumer_choices(
        p=u,
        rd=rd,
        rs=rs,
        t=t
    )

    return ("reply", utils.fname(), ) + to_reply

# -----------------------------------| active firm demands |-------------------------------------------------------- #


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
