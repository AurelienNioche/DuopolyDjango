from . import registration, info

# -------------------- registration ---------------------------------- #


def register_as_user(user_mail, nationality, gender, age, mechanical_id):

    return registration.register_as_user(
        user_mail=user_mail, nationality=nationality, gender=gender, age=age, mechanical_id=mechanical_id)


def registered_as_player(username):
    return registration.registered_as_player(username)


def proceed_to_registration_as_player(username):
    return registration.proceed_to_registration_as_player(username)


def connect(users, username, password):
    return registration.connect(users, username, password)


# -------------------- info ------------------------------------------- #


def room_available(rooms, players):
    return info.room_available(rooms=rooms, players=players)

#
# def missing_players(player_id):
#     return info.missing_players(player_id)
