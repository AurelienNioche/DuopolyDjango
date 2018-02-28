import os
import numpy as np
from django.utils import timezone

from utils import utils

from game.models import User

import game.room.state
import game.room.field_of_view

from . import mail, connection

__path__ = os.path.relpath(__file__)


def register_as_user(email, nationality, gender, age, mechanical_id):

    password = _generate_password()

    if mail.send(email=email, password=password):

        entry = User(
            username=email,
            email=email,
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


def get_init_info(u, opp, rm):

    consumer_seen_positions = game.room.field_of_view.compute(radius=rm.radius, to_send=True)

    # If room state is not end
    if rm.state != game.room.state.end:

        # get player's state
        end_vs_continue = u.state

        # Check if one of the player is a deserter
        if (u and u.deserter) or (opp and opp.deserter):
            # Return that the game ends
            end_vs_continue = game.room.state.end

    else:
        end_vs_continue = game.room.state.end

    return u.id, end_vs_continue, consumer_seen_positions


def proceed_to_registration_as_player(users, rooms, rounds, round_compositions, room_compositions, username):

    u = users.filter(username=username).first()

    if u.registered:

        utils.log(
            "{} is already registered but I will do as if it is not the case".format(username),
            f=utils.fname(), path=__path__)

        radius = rooms.get(room_id=u.room_id).radius
        consumer_seen_positions = game.room.field_of_view.compute(radius, to_send=True)

        return u.id, consumer_seen_positions

    # check if a room is available (and remove room with deserters)
    elif room_available(rooms=rooms, users=users):

        # Room ------------------------------------- #

        # Select the room
        rm = rooms.exclude(missing_players=0, opened=False).order_by("missing_players").first()

        # Decrease missing_players
        rm.missing_players -= 1

        # If round pve does not welcome additional players
        if rm.missing_players == 0:
            rm.opened = 0

        rm.save()

        # Room composition ----------------------- #

        rmc = room_compositions.filter(room_id=rm.id, available=True).first()
        rmc.user_id = u.id
        rmc.available = False
        rmc.save(update_fields=("user_id", "available"))

        # Round ------------------------------------------------- #

        rds = rounds.filter(room_id=rm.id).exclude(missing_players=0)

        rd_pve = rds.filter(pvp=False).first()
        rd_pvp = rds.filter(pvp=True).first()

        # Round Composition ---------------------------------------- #

        rc_pve = round_compositions.filter(round_id=rd_pve.id, available=True).first()
        rc_pve.user_id = u.id
        rc_pve.save()

        rc_pvp = round_compositions.filter(round_id=rd_pvp.id, available=True).first()
        rc_pvp.user_id = u.id
        rc_pvp.save()

        # User ----------------------------------------------------------------- #

        u.registered = True
        u.room_id = rm.id
        u.round_id = rd_pve.id
        u.firm_id = rc_pve.firm_id
        u.state = game.room.state.tutorial
        u.registration_time = timezone.now()
        u.save()

        # Get positions seen by consumers ----------------------- #

        consumer_seen_positions = game.room.field_of_view.compute(rm.radius, to_send=True)

        # Rounds ------------------------------------------- #

        utils.log("I registered {}".format(username), f=utils.fname(), path=__path__)

        return u.id, consumer_seen_positions

    else:
        return


def _generate_password():
    return '{:04d}'.format(np.random.randint(10000))


def room_available(rooms, users):

    entries = rooms.exclude(missing_players=0, opened=0)

    for rm in entries:
        u_room = users.filter(room_id=rm.id)
        if u_room:
            for u in u_room:
                if connection.banned(u=u):
                    # management.close(room_id=e.room_id)
                    rm.opened = 0
                    rm.save(update_fiels=("opened",))
                    break

    entries = entries.exclude(opened=0)

    utils.log("There are {} available rooms".format(len(entries)), f=utils.fname(), path=__path__)

    room_avail = int(len(entries) > 0)
    return room_avail
