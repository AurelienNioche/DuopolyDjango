from . import registration, info

# -------------------- registration ---------------------------------- #


def register_as_user(user_mail, nationality, gender, age, mechanical_id):

    return registration.register_as_user(
        user_mail=user_mail, nationality=nationality, gender=gender, age=age, mechanical_id=mechanical_id)


def send_password_again(user_mail, nationality, gender, age, mechanical_id):

    return registration.send_password_again(
        user_mail=user_mail, nationality=nationality, gender=gender, age=age, mechanical_id=mechanical_id)


def registered_as_player(username):
    return registration.registered_as_player(username)


def proceed_to_registration_as_player(username):
    return registration.proceed_to_registration_as_player(username)


def connect(username, password):
    return registration.connect(username, password)


# -------------------- info ------------------------------------------- #


def room_available():
    return info.room_available()


def missing_players(player_id):
    return info.missing_players(player_id)
