import os
import numpy as np
from django.utils import timezone

import utils.utils as utils

from game.models import Players, Users, Room

from game import round, player, room

from . import mail, info, field_of_view, state

__path__ = os.path.relpath(__file__)


def register_as_user(user_mail, nationality, gender, age, mechanical_id):

    user = Users.objects.filter(username=user_mail).first()

    if user is None:

        password = _generate_password()

        if mail.send(user_mail=user_mail, password=password):

            entry = Users(
                username=user_mail,
                email=user_mail,
                password=password,
                nationality=nationality,
                gender=gender,
                age=age,
                mechanical_id=mechanical_id,
                time_last_request=timezone.now(),
                last_request=utils.fname()
            )
            entry.save()

            return True

        else:
            return False
    else:
        return False


def send_password_again(user_mail, nationality, gender, age, mechanical_id):

    entry = Users.objects.filter(username=user_mail).first()

    if entry is not None:
        password = entry.password
        new = False

    else:
        password = _generate_password()
        new = True

    if mail.send(user_mail=user_mail, password=password):
        if new:
            entry = Users(
                username=user_mail,
                email=user_mail,
                password=password,
                nationality=nationality,
                gender=gender,
                age=age,
                mechanical_id=mechanical_id,
                time_last_request=timezone.now(),
                last_request=utils.fname()
            )
            entry.save()

        return True

    else:
        return False


def registered_as_player(username):

    player_id = Users.objects.filter(username=username).first().player_id
    pp = Players.objects.filter(player_id=player_id).first()

    if pp is not None:

        rm = Room.objects.get(room_id=pp.room_id)
        consumer_seen_positions = field_of_view.compute(room_id=pp.room_id, to_send=True)

        # get player's state
        end_vs_continue = pp.state

        # If room state is not end
        if rm.state != state.end:

            # Check if one of the player is a deserter
            player_0 = Users.objects.filter(player_id=rm.player_0).first()
            player_1 = Users.objects.filter(player_id=rm.player_1).first()

            if (player_0 and player_0.deserter) or (player_1 and player_1.deserter):
                # Return that the game ends
                end_vs_continue = state.end

        return pp.player_id, end_vs_continue, consumer_seen_positions


def proceed_to_registration_as_player(username):

    # check if a room is available
    if info.room_available():

        player_id = Users.objects.filter(username=username).first().player_id
        pp = Players.objects.filter(player_id=player_id).first()

        if pp is not None:

            utils.log(
                "{} is already registered but I will do as if it is not the case".format(username),
                f=utils.fname(), path=__path__)

        else:
            pp = _register_as_player(username=username)

        consumer_seen_positions = field_of_view.compute(room_id=pp.room_id, to_send=True)
        return pp.player_id, consumer_seen_positions


def connect(username, password):

    user = Users.objects.filter(username=username, password=password).first()

    return user is not None


def _register_as_player(username):

    utils.log("I registered {}".format(username), f=utils.fname(), path=__path__)

    rm = Room.objects.exclude(missing_players=0).exclude(opened=0).order_by("missing_players").first()

    if Players.objects.filter(player_id=rm.player_0).first():
        player_id = rm.player_1
    else:
        player_id = rm.player_0

    # Decrease missing_players
    rm.missing_players -= 1

    # If round pve does not welcome additional players
    if rm.missing_players == 0:
        rm.opened = 0

    # assign player_id to user
    user = Users.objects.get(username=username)
    user.player_id = player_id

    user.save(force_update=True)
    rm.save(force_update=True)

    round_id = round.dialog.include_players_into_round_compositions(
        room_id=rm.room_id, player_id=player_id, called_from=__path__ + ":" + utils.fname()
    )

    # When we create player entry, we associate him to a pve round id
    # because he needs to pass it in order to do pvp
    pp = Players(
        player_id=player_id,
        room_id=rm.room_id,
        round_id=round_id,
        state=state.tutorial,
        registration_time=timezone.now(),
    )

    pp.save()

    return pp


def _generate_password():
    return '{:04d}'.format(np.random.randint(10000))
