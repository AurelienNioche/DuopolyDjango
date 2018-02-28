import os
import numpy as np
from django.utils import timezone

from utils import utils

from game.models import User

from game import room

from . import mail, info, field_of_view, state

__path__ = os.path.relpath(__file__)


def register_as_user(user_mail, nationality, gender, age, mechanical_id):

    password = _generate_password()

    if mail.send(user_mail=user_mail, password=password):

        entry = User(
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


def registered_as_player(users, rooms, username):

    u = users.filter(username=username).first()

    if u.registered:

        rm = rooms.get(room_id=u.room_id)
        consumer_seen_positions = field_of_view.compute(room_id=rm.radius, to_send=True)

        # get player's state
        end_vs_continue = u.state

        # If room state is not end
        if rm.state != state.end:

            # Check if one of the player is a deserter
            player_0 = users.filter(id=rm.user_id_0).first()
            player_1 = users.filter(id=rm.user_id_1).first()

            if (player_0 and player_0.deserter) or (player_1 and player_1.deserter):
                # Return that the game ends
                end_vs_continue = state.end

        return u.id, end_vs_continue, consumer_seen_positions


def proceed_to_registration_as_player(users, players, rooms, rounds, round_compositions, username):

    u = users.filter(username=username).first()

    if u.registered:

        utils.log(
            "{} is already registered but I will do as if it is not the case".format(username),
            f=utils.fname(), path=__path__)

        radius = rooms.get(room_id=u.room_id).radius
        consumer_seen_positions = field_of_view.compute(radius, to_send=True)

        return u.id, consumer_seen_positions

    # check if a room is available
    elif info.room_available(rooms=rooms, players=players):

        rm = rooms.exclude(missing_players=0).exclude(opened=0).order_by("missing_players").first()

        if rm.user_id_0 == -1:
            rm.user_id_0 = u.id
        else:
            rm.user_id_1 = u.id

        # Decrease missing_players
        rm.missing_players -= 1

        # If round pve does not welcome additional players
        if rm.missing_players == 0:
            rm.opened = 0

        rm.save()

        consumer_seen_positions = field_of_view.compute(rm.radius, to_send=True)

        rds = rounds.filter(room_id=rm.room_id).exclude(missing_players=0)

        rd_pve = rds.filter(state=room.state.pve).first()
        rd_pvp = rds.filter(state=room.state.pvp).first()

        rd_pve.missing_players -= 1
        rd_pvp.missing_players -= 1

        # If round pve does not welcome additional players
        if rd_pve.missing_players == 0:
            rd_pve.opened = 0

        # If round pvp does not welcome additional players
        if rd_pvp.missing_players == 0:
            rd_pvp.opened = 0

        rd_pve.save()
        rd_pvp.save()

        # set player to agent_id firm 0 in round pve
        agent_id = 0
        rc_pve = round_compositions.filter(round_id=rd_pve.round_id, agent_id=agent_id).first()
        rc_pve.user_id = u.id

        agent_id = rd_pvp.missing_players  # Since already decreased, it will be either 0 or 1
        rc_pvp = round_compositions.filter(round_id=rd_pvp.round_id, agent_id=agent_id).first()
        rc_pvp.user_id = u.id

        rc_pve.save()
        rc_pvp.save()

        # assign player_id to user
        u.registered = True
        u.room_id = rm.room_id
        u.round_id = rd_pve.id
        u.state = room.state.tutorial
        u.registration_time = timezone.now()
        u.save()

        utils.log("I registered {}".format(username), f=utils.fname(), path=__path__)

        return u.id, consumer_seen_positions

    else:
        return


def connect(users, username, password):

    return users.filter(username=username, password=password).exists()


def _generate_password():
    return '{:04d}'.format(np.random.randint(10000))
