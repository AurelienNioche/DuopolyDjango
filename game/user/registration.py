import numpy as np
from django.utils import timezone

from utils import utils

from game.models import User

import game.room.state
import game.round.field_of_view

from game.user import mail, connection


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
            last_request=register_as_user.__name__
        )

        entry.save()
        return True
    else:
        return False


def get_init_info(u, opp, rm):

    consumer_seen_positions = game.round.field_of_view.compute(radius=rm.radius, to_send=True)

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


def proceed_to_registration_as_player(
        u, users, rooms_opened_with_missing_players,
        rounds_with_missing_players, round_compositions_available,
        room_compositions_available):

    # check if a room is available (and remove room with deserters)
    rooms = _close_rooms_with_banned_players(rooms_opened_with_missing_players, users)
    if not rooms:
        return

    # Room ------------------------------------- #

    # Select the room
    rm = rooms.order_by("missing_players").first()

    # Decrease missing_players
    rm.missing_players -= 1
    rm.save(update_fields=["missing_players"])

    # Room composition ----------------------- #

    rmc = room_compositions_available.filter(room_id=rm.id).first()
    rmc.user_id = u.id
    rmc.available = False
    rmc.save(update_fields=("user_id", "available"))

    # Round ------------------------------------------------- #

    rds = rounds_with_missing_players.filter(room_id=rm.id)

    rd_pve = rds.filter(pvp=False).first()
    rd_pve.missing_players -= 1
    rd_pve.save(update_fields=["missing_players"])

    rd_pvp = rds.filter(pvp=True).first()
    rd_pvp.missing_players -= 1
    rd_pvp.save(update_fields=["missing_players"])

    # Round Composition ---------------------------------------- #

    rc_pve = round_compositions_available.filter(round_id=rd_pve.id).first()
    rc_pve.user_id = u.id
    rc_pve.available = False
    rc_pve.save(update_fields=["user_id", "available"])

    rc_pvp = round_compositions_available.filter(round_id=rd_pvp.id).first()
    rc_pvp.user_id = u.id
    rc_pvp.available = False
    rc_pvp.save(update_fields=["user_id", "available"])

    # User ----------------------------------------------------------------- #

    u.registered = True
    u.room_id = rm.id
    u.round_id = rd_pve.id
    u.firm_id = rc_pve.firm_id
    u.state = game.room.state.tutorial
    u.registration_time = timezone.now()
    u.save(update_fields=["registered", "room_id", "round_id", "firm_id", "state", "registration_time"])

    # Get positions seen by consumers ----------------------- #

    consumer_seen_positions = game.round.field_of_view.compute(rm.radius, to_send=True)

    # Rounds ------------------------------------------- #

    utils.log("I registered {}".format(u.username), f=proceed_to_registration_as_player)

    return u.id, game.room.state.tutorial, consumer_seen_positions


def _generate_password():
    return '{:04d}'.format(np.random.randint(10000))


def room_available(rooms_opened_with_missing_players, users):

    rooms = _close_rooms_with_banned_players(rooms_opened_with_missing_players, users)

    utils.log("There are {} available rooms".format(len(rooms)), f=room_available)

    return len(rooms) > 0


def _close_rooms_with_banned_players(rooms_opened_with_missing_players, users):

    for rm in rooms_opened_with_missing_players:
        u_room = users.filter(room_id=rm.id)
        if u_room:
            for u in u_room:
                connection.banned(u=u, rm=rm)

    return rooms_opened_with_missing_players.exclude(opened=False)  # Exclude rooms closed above
