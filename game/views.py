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
import game.room.dashboard


@csrf_exempt
def client_request(request):

    """
    main method taking request from client
    and returning
    :param request:
    :return: response
    """

    is_http_request = False

    if hasattr(request, 'GET'):
        request = request.GET
        is_http_request = True

    # Log
    utils.log("Request: {}".format(list(request.items())), f=client_request)

    error, demand, users, u, opp, rm = _verification(request)

    if error is not None:
        to_reply = "/".join(["reply", demand, str(error)])

    else:
        try:
            # Retrieve functions declared in the current script
            functions = {f_name: f for f_name, f in globals().items() if not f_name.startswith("_")}
            # Retrieve demanded function
            func = functions[demand]
            f_return = func(request=request, users=users, u=u, opp=opp, rm=rm)
            args = [str(i) for i in f_return] if f_return is not None else []
            to_reply = "/".join(["reply", demand] + args)

        except KeyError:
            raise Exception("Bad demand")

    # Log
    if "username" in request:
        identifier = request['username']
    elif "player_id" in request:
        identifier = request['player_id']
    else:
        identifier = ""

    utils.log("I will reply '{}' to player {}.".format(to_reply, identifier), f=client_request)

    if is_http_request:
        to_reply = HttpResponse(to_reply)
        to_reply["Access-Control-Allow-Credentials"] = "true"
        to_reply["Access-Control-Allow-Headers"] = "Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time"
        to_reply["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        to_reply["Access-Control-Allow-Origin"] = "*"

    return to_reply


def _verification(request):

    demand = request.get("demand")
    player_id = request.get("player_id")

    # Get data from table
    users = User.objects.all()
    error, u, opp, rm = (None, ) * 4

    if player_id:
         u = users.get(id=player_id)

    else:
        username = request.get("username")
        if username:
            username = username.lower()
            u = users.filter(username=username).first()  # Could be none in case of typo
        else:
            email = request.get("email")
            if email is not None:
                email.lower()
                u = users.filter(email=email).first()  # Could be None

    if u:

        rm = Room.objects.filter(id=u.room_id).first()  # Could be None

        if rm:
            rc_opp = RoomComposition.objects.filter(room_id=rm.id, available=False).exclude(user_id=u.id).first()
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


def trial_registration(**kwargs):

    n_player = int(kwargs['request']['n_player'])
    usernames, passwords = game.user.registration.trial_registration(n_player=n_player)

    return str(usernames), str(passwords)


def register(**kwargs):

    request, u = (kwargs.get(i) for i in ("request", "u"))

    email = request["email"].lower()
    nationality = request["nationality"]
    gender = request["gender"]
    age = request["age"]
    mechanical_id = request["mechanical_id"]

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

    email = request["email"].lower()
    nationality = request["nationality"],
    gender = request["gender"],
    age = request["age"],
    mechanical_id = request["mechanical_id"]

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
    rooms = Room.objects.exclude(missing_players=0).exclude(opened=0)

    rsp = game.user.registration.room_available(rooms_opened_with_missing_players=rooms, users=users)

    return int(rsp),


def proceed_to_registration_as_player(**kwargs):

    u, opp, rm, users = (kwargs.get(i) for i in ("u", "opp", "rm", "users"))

    if u.registered:
        rsp = game.user.registration.get_init_info(u=u, opp=opp, rm=rm)

    else:
        with transaction.atomic():

            rm = Room.objects.filter(id=u.room_id).first() if u.demo else None

            rooms = Room.objects.select_for_update().exclude(missing_players=0).exclude(opened=0)
            rounds = Round.objects.select_for_update().exclude(missing_players=0)
            round_compositions = RoundComposition.objects.select_for_update().filter(available=True)
            room_compositions = RoomComposition.objects.select_for_update().filter(available=True)

            rsp = game.user.registration.proceed_to_registration_as_player(
                users=users, rooms_opened_with_missing_players=rooms,
                rounds_with_missing_players=rounds,
                round_compositions_available=round_compositions,
                room_compositions_available=room_compositions,
                u=u,
                rm=rm)

    if rsp:
        return (1, ) + rsp

    else:
        return 0,


def connect(**kwargs):

    request, users = (kwargs.get(i) for i in ("request", "users"))

    # Get info from POST
    username = request["username"].lower()
    password = request["password"]

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

# def tutorial_done(**kwargs):
#
#     game.round.state.go_to_next_round(u=kwargs["u"], opp=kwargs["opp"], rm=kwargs["rm"])


def submit_tutorial_progression(**kwargs):

    request, u = (kwargs.get(i) for i in ("request", "u"))

    tutorial_progression = float(request["tutorial_progression"].replace(",", "."))

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

    request, u, opp, rm = (kwargs.get(i) for i in ("request", "u", "opp", "rm"))

    t = int(request["t"])

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    return game.round.play.ask_firm_passive_opponent_choice(u=u, rd=rd, rs=rs, t=t, rm=rm, opp=opp)


# def ask_firm_passive_consumer_choices(**kwargs):
#
#     """
#     Called by a passive firm in order to get consumers' firm choices.
#     """
#
#     request, u, opp, rm = (kwargs.get(i) for i in ("request", "u", "opp", "rm"))
#
#     t = int(request["t"])
#
#     rd = Round.objects.get(id=u.round_id)
#     rs = RoundState.objects.get(round_id=u.round_id, t=t)
#
#     return game.round.play.ask_firm_passive_consumer_choices(u=u, opp=opp, rm=rm, rd=rd, rs=rs, t=t)

# -----------------------------------| active firm demands |-------------------------------------------------------- #


def ask_firm_active_choice_recording(**kwargs):

    """
    called by active firm
    """

    request, u, opp, rm = (kwargs.get(i) for i in ("request", "u", "opp", "rm"))

    t = int(request["t"])
    position = int(request["position"])
    price = int(request["price"])

    rd = Round.objects.get(id=u.round_id)
    rs = RoundState.objects.get(round_id=u.round_id, t=t)

    return game.round.play.ask_firm_active_choice_recording(
        u=u, rd=rd, rs=rs, t=t, position=position, price=price, opp=opp, rm=rm)


# def ask_firm_active_consumer_choices(**kwargs):
#
#     """
#     called by active firm
#     """
#
#     request, u, opp, rm = (kwargs.get(i) for i in ("request", "u", "opp", "rm"))
#
#     t = int(request["t"])
#
#     rd = Round.objects.get(id=u.round_id)
#     rs = RoundState.objects.get(round_id=u.round_id, t=t)
#
#     return game.round.play.ask_firm_active_consumer_choices(u, opp, rm, rd, rs, t)
