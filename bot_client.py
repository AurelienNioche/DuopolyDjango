import requests
import enum


# --------------- Sign in ----------------- #

class KeySi:

    demand = "demand"


class DemandSi:

    register = "register"
    send_password_again = "send_password_again"


class ErrorSi:

    sending_aborted = "sending_aborted"
    already_exists = "already_exists"


# -------------- Log in --------------------- #

class KeyLi:

    demand = "demand"
    username = "username"
    password = "password"


class DemandLi:

    connect = "connect"

# -------------- Look for Playing ---------- #


class CodeErrorLfp:

    opponent_disconnected = -3
    player_disconnected = -4
    no_other_player = -5


class DemandLfp:

    registered_as_player = "registered_as_player"
    room_available = "room_available"
    missing_players = "missing_players"
    proceed_to_registration_as_player = "proceed_to_registration_as_player"
    player_info = "player_info"


class KeyLfp:

    demand = "demand"
    username = "username"
    player_id = "player_id"


# ---------------- Firm ---------------------- #


class DemandF:
    tutorial_done = "tutorial_done"
    ask_firm_init = "ask_firm_init"
    ask_firm_passive_opponent_choice = "ask_firm_passive_opponent_choice"
    ask_firm_passive_consumer_choices = "ask_firm_passive_consumer_choices"
    ask_firm_active_choice_recording = "ask_firm_active_choice_recording"
    ask_firm_active_consumer_choices = "ask_firm_active_consumer_choices"
    submit_tutorial_progression = "submit_tutorial_progression"


class KeyF:

    demand = "demand"
    username = "username"
    player_id = "player_id"
    t = "t"
    position = "position"
    price = "price"
    tutorial_progression = "tutorial_progression"



class CodeErrorF:

    haveToWait = -1
    timeSuperior = -2
    opponentDisconnected = -3
    playerDisconnected = -4


class State(enum.Enum):

    pass


def print_reply(f):
    def wrapper(*args):
        print("{}: {}".format(f.__name__, *args[1:]))
        return f(*args)
    return wrapper


class BotClient:

    def __init__(self, username="nioche.aurelien@gmail.com", password="6114"):

        self.username = username
        self.password = password

        self.player_id = None

    def _request(self, data):

        try:

            url = "http://127.0.0.1:8000/client_request/"
            r = requests.post(url, data=data)
            rsp_parts = r.text.split("/")

            if len(rsp_parts) > 1 and rsp_parts[0] == "reply":

                if len(rsp_parts) <= 2:
                    return getattr(self, rsp_parts[1])()

                else:
                    return getattr(self, "reply_{}".format(rsp_parts[1]))(*rsp_parts[2:])
            else:
                print(r.text)

        except requests.exceptions.ConnectionError as e:
            print(e)

    def connect(self):

        return self._request({
            KeyLi.demand: DemandLi.connect,
            KeyLi.username: self.username,
            KeyLi.password: self.password

        })

    @print_reply
    def reply_connect(self, *args):
        return int(args[0])

    def registered_as_player(self):

        return self._request({
            KeyLfp.demand: DemandLfp.registered_as_player,
            KeyLfp.username: self.username
        })

    @print_reply
    def reply_registered_as_player(self, *args):
        if int(args[0]):
            self.player_id = args[1]
        return int(args[0])

    def room_available(self):

        return self._request({
            KeyLfp.demand: DemandLfp.room_available,
            KeyLfp.username: self.username
        })

    @print_reply
    def reply_room_available(self, *args):
        return int(args[0])

    def proceed_to_registration_as_player(self):

        return self._request({
            KeyLfp.demand: DemandLfp.proceed_to_registration_as_player,
            KeyLfp.username: self.username
        })

    @print_reply
    def reply_proceed_to_registration_as_player(self, *args):
        if int(args[0]):
            self.player_id = args[1]
        return int(args[0])

    def missing_players(self):

        return self._request({
            KeyLfp.demand: DemandLfp.missing_players,
            KeyLfp.player_id: self.player_id
        })

    @print_reply
    def reply_missing_players(self, *args):
        return int(args[0])


def main():

    b = BotClient()

    # Make request until connected
    connected = 0
    while not connected:
        connected = b.connect()

    # Look if already registered
    registered = b.registered_as_player()

    # If not already registered
    if not registered:

        # While there is no room available, ask for it
        place = 0
        while place == 0:
            place = b.room_available()

            # If there is place, try to register
            if place:
                registered = b.proceed_to_registration_as_player()
                if registered:
                    break

    # Once registered, ask for missing players
    m_p = b.missing_players()
    while m_p != 0:
        m_p = b.missing_players()

    print("Let's play!")


if __name__ == "__main__":

    main()
