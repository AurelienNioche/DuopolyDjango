from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from utils import utils

from game.models import User, Room, Round, RoundComposition, RoundState, RoomComposition

import game.user.connection
import game.user.registration
import game.user.mail
import game.round.play
import game.round.state


@csrf_exempt
def client_request(request):

    """
    main method taking request from client
    and returning
    :param request:
    :return: response
    """

    # Log
    utils.log("Post request: {}".format(list(request.POST.items())), f=client_request)

    error, demand, users, u, opp, rm = _verification(request)
    if error is not None:
        return "reply", demand, error

    try:
        # Retrieve functions declared in the current script
        functions = {f_name: f for f_name, f in globals().items() if not f_name.startswith("_")}
        # Retrieve demanded function
        func = functions[demand]

    except KeyError:
        raise Exception("Bad demand")

    f_return = func(request=request, users=users, u=u, opp=opp, rm=rm)
    args = [str(i) for i in f_return] if f_return is not None else []
    to_reply = "/".join(["reply", demand] + args)

    # Log
    utils.log("I will reply '{}' to client.".format(to_reply), f=client_request)

    response = HttpResponse(to_reply)
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Headers"] = "Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Origin"] = "*"

    return response


def _verification(request):

    demand = request.POST["demand"]
    player_id = request.POST.get("player_id")

    # Get data from table
    users = User.objects.all()

    error, u, opp, rm = None, None, None, None

    if player_id:
        u = users.get(id=player_id)

    else:
        username = request.POST.get("username")
        if username:
            u = users.get(username=username)
        else:
            email = request.POST.get("email")
            u = users.filter(email=email).first()  # Could be None

    if u:

        rm = Room.objects.filter(id=u.room_id).first()  # Could be None
        if rm:
            rc_opp = RoomComposition.objects.filter(room_id=rm.id).exclude(user_id=u.id).first()
            if rc_opp:
                opp = users.get(id=rc_opp.user_id)

        if demand in ("register", "send_password_again", "room_available", "proceed_to_registration_as_player",
                      "connect", "registered_as_player", "tutorial_done", "submit_tutorial_progression"):
            # Check connection (basic as 'rm' will be None)
            game.user.connection.check(
                demand=demand,
                users=users,
                u=u
            )
        else:
            # Check connection
            error = game.user.connection.check(
                demand=demand,
                users=users,
                u=u,
                rm=rm,
                opp=opp
            )

    return error, demand, users, u, opp, rm


# ----------------------| Demands relative to registration |--------------------------------------------------------- #


def register(**kwargs):

    request, u = (kwargs.get(i) for i in ("request", "u"))

    email = request.POST["email"].lower()
    nationality = request.POST["nationality"]
    gender = request.POST["gender"]
    age = request.POST["age"]
    mechanical_id = request.POST["mechanical_id"]

    # Do stuff
    if u:
        return 0, "already_exists"

    if game.user.registration.register_as_user(
            email=email,
            nationality=nationality,
            gender=gender,
            age=age,
            mechanical_id=mechanical_id):

        return 1,

    else:
        return 0, "sending_aborted"


def send_password_again(**kwargs):

    """
    Get called when user wants to renew its password
    :return: 1 if it worked, 0 else
    """
    request, u = [kwargs.get(i) for i in ("request", "u")]

    email = request.POST["email"].lower()
    nationality = request.POST["nationality"],
    gender = request.POST["gender"],
    age = request.POST["age"],
    mechanical_id = request.POST["mechanical_id"]

    # If already registered
    if u:
        went_well = game.user.mail.send(email=email, password=u.password)

    else:
        went_well = game.user.registration.register_as_user(
            email=email,
            nationality=nationality,
            gender=gender,
            age=age,
            mechanical_id=mechanical_id
        )

    return int(went_well),

# ----------------------------------| Participation |--------------------------------------------------------------- #


def room_available(**kwargs):

    users = kwargs["users"]

    # Get data from table
    rooms = Room.objects.exclude(missing_players=0, opened=0)

    # Return 'True' if a room is available
    rsp = game.user.registration.room_available(rooms_opened_with_missing_players=rooms, users=users)

    return int(rsp),


def proceed_to_registration_as_player(**kwargs):

    u, opp, rm, users = (kwargs.get(i) for i in ("u", "opp", "rm", "users"))

    if u.registered:
        rsp = game.user.registration.get_init_info(u=u, opp=opp, rm=rm)

    else:
        with transaction.atomic():

            rooms = Room.objects.select_for_update().exclude(missing_players=0, opened=0)
            rounds = Round.objects.select_for_update().exclude(missing_players=0)
            round_compositions = RoundComposition.objects.select_for_update().filter(available=True)
            room_compositions = RoomComposition.objects.select_for_update().filter(available=True)

            rsp = game.user.registration.proceed_to_registration_as_player(
                users=users, rooms_opened_with_missing_players=rooms,
                rounds_with_missing_players=rounds,
                round_compositions_available=round_compositions,
                room_compositions_available=room_compositions,
                u=u)

    if rsp:
        return (1, ) + rsp

    else:
        return 0,


def connect(**kwargs):

    request, users = (kwargs.get(i) for i in ("request", "users"))

    # Get info from POST
    username = request.POST["username"].lower()
    password = request.POST["password"]

    u = users.filter(username=username, password=password).first()  # Could be None

    return int(u is not None),


def registered_as_player(**kwargs):

    u, opp, rm = (kwargs.get(i) for i in ("u", "opp", "rm"))

    if u.registered:

        rsp = game.user.registration.get_init_info(u=u, opp=opp, rm=rm)
        return (1, ) + rsp

    else:
        return 0,


def missing_players(**kwargs):

    return kwargs["rm"].missing_players,


# ----------------------------------| Demand relatives to Tutorial  |------------------------------------------------- #

def tutorial_done(**kwargs):

    game.round.state.go_to_next_round(u=kwargs["u"], opp=kwargs["opp"], rm=kwargs["rm"])


def submit_tutorial_progression(**kwargs):

    request, u = (kwargs.get(i) for i in ("request", "u"))

    tutorial_progression = float(request.POST["tutorial_progression"].replace(",", "."))

    u.tutorial_progression = tutorial_progression * 100
    u.save(update_fields=("tutorial_progression", ))


# ------------------------| Firms ask for their init info at the beginning of each round |-------------------------- #

def ask_firm_init(**kwargs):

    request, u, opp, rm = (kwargs.get(i) for i in ("request", "u", "opp", "rm"))

    rd = Round.objects.get(id=u.round_id)
    rd_opp = Round.objects.filter(id=opp.round_id).first() if opp is not None else None
    rs = RoundState.objects.get(round_id=u.round_id, t=rd.t)

    return game.round.play.ask_firm_init(u=u, opp=opp, rd_opp=rd_opp, rm=rm, rd=rd, rs=rs)

# ----------------------------------| passive firm demands |----------------------------------------------------- #


def ask_firm_passive_opponent_choice(**kwargs):

    """
    called by a passive firm
    """

    request, u = (kwargs.get(i) for i in ("request", "u"))

    t = int(request.POST["t"])

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    return game.round.play.ask_firm_passive_opponent_choice(u=u, rd=rd, rs=rs, t=t)


def ask_firm_passive_consumer_choices(**kwargs):

    """
    Called by a passive firm in order to get consumers' firm choices.
    """

    request, u, opp, rm = (kwargs.get(i) for i in ("request", "u", "opp", "rm"))

    t = int(request.POST["t"])

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    return game.round.play.ask_firm_passive_consumer_choices(u=u, opp=opp, rm=rm, rd=rd, rs=rs, t=t)

# -----------------------------------| active firm demands |-------------------------------------------------------- #


def ask_firm_active_choice_recording(**kwargs):

    """
    called by active firm
    """

    request, u = (kwargs.get(i) for i in ("request", "u"))

    t = int(request.POST["t"])
    position = int(request.POST["position"])
    price = int(request.POST["price"])

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    return game.round.play.ask_firm_active_choice_recording(u=u, rd=rd, rs=rs, t=t, position=position, price=price)


def ask_firm_active_consumer_choices(**kwargs):

    """
    called by active firm
    """

    request, u, opp, rm = (kwargs.get(i) for i in ("request", "u", "opp", "rm"))

    t = int(request.POST["t"])

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    return game.round.play.ask_firm_active_consumer_choices(u, opp, rm, rd, rs, t)
