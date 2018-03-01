from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import os

from utils import utils

from game.models import User, Room, Round, RoundComposition, RoundState, RoomComposition

import game.player.connection
import game.player.registration
import game.player.mail
import game.round.client
import game.round.state

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

    email = request.POST["email"].lower()
    nationality = request.POST["nationality"]
    gender = request.POST["gender"]
    age = request.POST["age"]
    mechanical_id = request.POST["mechanical_id"]

    # Get data from table
    users = User.objects.all()
    u = users.filter(email=email).first()  # Could be None

    # Do stuff
    if u:
        # Check connection (basic as 'rm' will be None)
        game.player.connection.check(
            called_from=connect.__name__,
            users=users,
            u=u
        )
        return "reply", utils.fname(), 0, "already_exists"

    if game.player.registration.register_as_user(
            email=email,
            nationality=nationality,
            gender=gender,
            age=age,
            mechanical_id=mechanical_id):

        return "reply", utils.fname(), 1

    else:
        return "reply", utils.fname(), 0, "sending_aborted"


def send_password_again(request):

    """
    Get called when user wants to renew its password
    :param request:
    :return: 1 if it worked, 0 else
    """

    email = request.POST["email"].lower()
    nationality = request.POST["nationality"],
    gender = request.POST["gender"],
    age = request.POST["age"],
    mechanical_id = request.POST["mechanical_id"]

    # Get data from table
    users = User.objects.all()

    u = users.filter(email=email).first()

    # If already registered
    if u:
        # Check connection (basic as 'rm' will be None)
        game.player.connection.check(
            called_from=connect.__name__,
            users=users,
            u=u
        )
        went_well = game.player.mail.send(email=email, password=u.password)

    else:
        went_well = game.player.registration.register_as_user(
            email=email,
            nationality=nationality,
            gender=gender,
            age=age,
            mechanical_id=mechanical_id
        )

    return "reply", utils.fname(), int(went_well)

# ----------------------------------| Participation |--------------------------------------------------------------- #


def room_available(request):

    # Get info from POST
    username = request.POST["username"].lower()

    # Get data from table
    users = User.objects.all()
    u = users.filter(username=username).first()

    # Check connection (basic as 'rm' will be None)
    game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u
    )

    # Do specific stuff --------------------- #

    # Get data from table
    rooms = Room.objects.all()

    # Return 'True' if a room is available
    rsp = game.player.registration.room_available(rooms=rooms, users=users)

    return "reply", utils.fname(), int(rsp)


def proceed_to_registration_as_player(request):

    # Get info from POST
    username = request.POST["username"].lower()

    # Get data from table
    users = User.objects.all()
    u = users.filter(username=username).first()

    # Check connection (basic as 'rm' will be None)
    game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u)

    with transaction.atomic():

        users = User.objects.select_for_update().all()
        rooms = Room.objects.select_for_update().all()
        rounds = Round.objects.select_for_update().all()
        round_compositions = RoundComposition.objects.select_for_update().all()
        room_compositions = RoomComposition.objects.select_for_update().all()

        rsp = game.player.registration.proceed_to_registration_as_player(
            users=users, rooms=rooms, rounds=rounds, round_compositions=round_compositions,
            room_compositions=room_compositions,
            username=username)

    if rsp:
        return ("reply", utils.fname(), 1) + rsp

    else:
        return "reply", utils.fname(), 0


def connect(request):

    # Get info from POST
    username = request.POST["username"].lower()
    password = request.POST["password"]

    # Get data from table
    users = User.objects.all()
    u = users.filter(username=username, password=password).first()  # Could be None

    if u:
        # Check connection (basic as 'rm' will be None)
        game.player.connection.check(
            called_from=connect.__name__,
            users=users,
            u=u
        )
        return "reply", utils.fname(), 1

    else:
        return "reply", utils.fname(), 0


def registered_as_player(request):

    # Get info from POST
    username = request.POST["username"].lower()

    # Get data from table
    users = User.objects.all()

    u = users.filter(username=username).first()

    # Check connection (basic as 'rm' will be None)
    game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u
    )

    # Do specific stuff ------------------------------- #

    if u.registered:

        rm = Room.objects.filter(id=u.room_id).first()
        opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

        rsp = game.player.registration.get_init_info(u=u, opp=opp, rm=rm)
        return ("reply", utils.fname(), 1) + rsp

    else:
        return "reply", utils.fname(), 0


def missing_players(request):

    player_id = request.POST["player_id"]

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()
    rm = Room.objects.filter(id=u.room_id).first()
    opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

    # Check connection
    ok, error = game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u,
        rm=rm,
        opp=opp
    )
    if not ok:
        return "reply", utils.fname(), error

    # Do specific stuff --------------------- #

    return "reply", utils.fname(), rm.missing_players


# ----------------------------------| Demand relatives to Tutorial  |------------------------------------------------- #

def tutorial_done(request):

    player_id = request.POST["player_id"]

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()

    # Check connection (basic as the client cannot handle error at this time point)
    game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u
    )

    # Do specific stuff --------------------- #

    rm = Room.objects.filter(id=u.room_id).first()
    opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

    game.round.state.go_to_next_round(u=u, opp=opp, rm=rm)

    return "reply", utils.fname()


def submit_tutorial_progression(request):

    player_id = request.POST["player_id"]
    tutorial_progression = float(request.POST["tutorial_progression"].replace(",", "."))

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()

    # Check connection (basic as the client cannot handle error at this time point)
    game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u
    )

    # Do specific stuff --------------------- #

    u.tutorial_progression = tutorial_progression * 100
    u.save(update_fields=("tutorial_progression", ))

    return "reply", utils.fname()


# ------------------------| Firms ask for their init info at the beginning of each round |-------------------------- #

def ask_firm_init(request):

    player_id = request.POST["player_id"]

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()
    rm = Room.objects.filter(id=u.room_id).first()
    opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

    # Check connection
    ok, error = game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u,
        rm=rm,
        opp=opp
    )
    if not ok:
        return "reply", utils.fname(), error

    # Do specific stuff --------------------- #

    rd = Round.objects.get(id=u.round_id)
    rd_opp = Round.objects.filter(id=opp.round_id).first() if opp is not None else None
    rs = RoundState.objects.get(round_id=u.round_id, t=rd.t)

    to_reply = game.round.client.ask_firm_init(u=u, rd_opp=rd_opp, rm=rm, rd=rd, rs=rs)

    return ("reply", utils.fname(), ) + to_reply

# ----------------------------------| passive firm demands |----------------------------------------------------- #


def ask_firm_passive_opponent_choice(request):

    """
    called by a passive firm
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()
    rm = Room.objects.filter(id=u.room_id).first()
    opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

    # Check connection
    ok, error = game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u,
        rm=rm,
        opp=opp
    )
    if not ok:
        return "reply", utils.fname(), error

    # Do specific stuff --------------------- #

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    to_reply = game.round.client.ask_firm_passive_opponent_choice(
        u=u, rd=rd, rs=rs, t=t
    )

    return ("reply", utils.fname(), ) + to_reply


def ask_firm_passive_consumer_choices(request):

    """
    Called by a passive firm in order to get consumers' firm choices.
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()
    rm = Room.objects.filter(id=u.room_id).first()
    opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

    # Check connection
    ok, error = game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u,
        rm=rm,
        opp=opp
    )
    if not ok:
        return "reply", utils.fname(), error

    # Do specific stuff --------------------- #

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    to_reply = game.round.client.ask_firm_passive_consumer_choices(u=u, opp=opp, rm=rm, rd=rd, rs=rs, t=t)

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

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()
    rm = Room.objects.filter(id=u.room_id).first()
    opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

    # Check connection
    ok, error = game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u,
        rm=rm,
        opp=opp
    )
    if not ok:
        return "reply", utils.fname(), error

    # Do specific stuff --------------------- #

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    to_reply = game.round.client.ask_firm_active_choice_recording(
        u=u, rd=rd, rs=rs, t=t, position=position, price=price
    )

    return ("reply", utils.fname(), ) + to_reply


def ask_firm_active_consumer_choices(request):

    """
    called by active firm
    """

    player_id = request.POST["player_id"]
    t = int(request.POST["t"])

    # Get data from table
    users = User.objects.all()

    u = users.filter(id=player_id).first()
    rm = Room.objects.filter(id=u.room_id).first()
    opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()

    # Check connection
    ok, error = game.player.connection.check(
        called_from=connect.__name__,
        users=users,
        u=u,
        rm=rm,
        opp=opp
    )
    if not ok:
        return "reply", utils.fname(), error

    # Do specific stuff --------------------- #

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    to_reply = game.round.client.ask_firm_active_consumer_choices(u, opp, rm, rd, rs, t)

    return ("reply", utils.fname(), ) + to_reply
