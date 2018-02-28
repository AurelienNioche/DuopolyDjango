import requests
import enum
import multiprocessing as ml
import numpy as np

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


class FirmState:
    passive = "passive"
    active = "active"


def print_reply(f):

    def wrapper(*args):
        print("{} {}: {}".format(args[0].username, f.__name__, *args[1:]))
        return f(*args)

    return wrapper


class BotClient:

    def __init__(self, url="http://51.15.6.148/client_request/",
                 username="nioche.aurelien@gmail.com", password="6114"):

        self.url = url
        self.username = username
        self.password = password

        self.n_prices = 11
        self.n_positions = 21

        self.t = None
        self.state = None
        self.player_id = None
        self.game_state = None

    def _request(self, data):

        try:

            r = requests.post(self.url, data=data)
            rsp_parts = r.text.split("/")

            if len(rsp_parts) > 1 and rsp_parts[0] == "reply":

                if rsp_parts[1] == "error":
                    self._request(data)

                elif len(rsp_parts) <= 2:
                    return getattr(self, rsp_parts[1])()

                else:
                    return getattr(self, "reply_{}".format(rsp_parts[1]))(*rsp_parts[2:])
            else:
                if len(r.text) < 100:
                    print(self.username, r.text)
                else:
                    print(self.username, "Length is too long, probably received an error in html format")

        except requests.exceptions.ConnectionError as e:
            print(e)

    def _increment_time_step(self):
        self.t += 1
        self.state = "active" if self.state == "passive" else "passive"

    def register_(self):

        return self._request({
            KeySi.demand: DemandSi.register,
            KeySi.email: self.username,
        })

    @print_reply
    def reply_register(self, *args):
        return int(args[0])


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

    def submit_tutorial_progression(self):
        return self._request({
            KeyF.demand: DemandF.submit_tutorial_progression,
            KeyF.player_id: self.player_id,
            KeyF.tutorial_progression: 100.00,
        })

    @print_reply
    def reply_submit_tutorial_progression(self, *args):
        return True

    def tutorial_done(self):
        return self._request({
            KeyF.demand: DemandF.tutorial_done,
            KeyF.player_id: self.player_id
        })

    @print_reply
    def reply_tutorial_done(self, *args):
        return True

    def ask_firm_init(self):
        return self._request({
            KeyF.demand: DemandF.ask_firm_init,
            KeyF.player_id: self.player_id
        })

    @print_reply
    def reply_ask_firm_init(self, *args):
        self.t = int(args[0])
        self.state = args[1]
        return True

    def ask_firm_passive_opponent_choice(self):
        return self._request({
            KeyF.demand: DemandF.ask_firm_passive_opponent_choice,
            KeyF.player_id: self.player_id
        })

    @print_reply
    def reply_ask_firm_passive_opponent_choice(self, *args):
        return True

    def ask_firm_passive_consumer_choices(self):
        return self._request({
            KeyF.demand: DemandF.ask_firm_passive_consumer_choices,
            KeyF.player_id: self.player_id
        })

    @print_reply
    def reply_ask_firm_passive_consumer_choices(self, *args):
        self._increment_time_step()
        if int(args[-1]):
            return "end_t"
        return True

    def ask_firm_active_choice_recording(self):
        return self._request({
            KeyF.demand: DemandF.ask_firm_active_choice_recording,
            KeyF.player_id: self.player_id,
            KeyF.position: np.random.randint(self.n_positions),
            KeyF.price: np.random.randint(self.n_prices)
        })

    @print_reply
    def reply_ask_firm_active_choice_recording(self, *args):
        return True

    def ask_firm_active_consumer_choices(self):
        return self._request({
            KeyF.demand: DemandF.ask_firm_active_consumer_choices,
            KeyF.player_id: self.player_id
        })

    @print_reply
    def reply_ask_firm_active_consumer_choices(self, *args):
        self._increment_time_step()
        if int(args[-1]):
            return "end_t"
        return True


class BotProcess(ml.Process):

    def __init__(self, url, start_event, username, password):
        super().__init__()
        self.start_event = start_event
        self.b = BotClient(url=url, username=username, password=password)

    def run(self):

        self.b.register_as_user()

        # self.before_playing()
        # self.tutorial()

        # end = False
        # while not end:
        #     end = self.play()

    def before_playing(self):

        # Make request until connected
        connected = 0
        while not connected:
            connected = self.b.connect()

        # Look if already registered
        registered = self.b.registered_as_player()

        # If not already registered
        if not registered:

            while True:

                place = self.b.room_available()

                # If there is place, try to register
                if place:
                    self.start_event.wait()
                    registered = self.b.proceed_to_registration_as_player()
                    if registered:
                        break

        # Once registered, ask for missing players
        m_p = self.b.missing_players()
        while m_p != 0:
            m_p = self.b.missing_players()

        self.b.game_state = "tutorial"

        print("Let's play!")

    def tutorial(self):

        done = False
        while not done:
            done = self.b.tutorial_done()

        self.b.game_state = "pve"

    def play(self):

        init = False
        while not init:
            init = self.b.ask_firm_init()

        while True:

            if self.b.state == "active":

                recorded = False
                while not recorded:
                    recorded = self.b.ask_firm_active_choice_recording()

                consumer_choices = False
                while not consumer_choices:
                    consumer_choices = self.b.ask_firm_active_consumer_choices()

                if consumer_choices == "end_t":
                    break

            else:

                opp_choice = False
                while not opp_choice:
                    opp_choice = self.b.ask_firm_passive_opponent_choice()

                consumer_choices = False
                while not consumer_choices:
                    consumer_choices = self.b.reply_ask_firm_passive_consumer_choices()

                if consumer_choices == "end_t":
                    break

        self.b.game_state = "pvp" if self.b.game_state == "pve" else "end"

        if self.b.game_state == "end":
            return True


def main():

    url = "http://127.0.0.1:8000/client_request/"
    # url = "http://51.15.6.148/client_request/",

    n_accounts = 1

    start_event = ml.Event()

    for n in range(n_accounts):

        pwd = "{}".format(n).zfill(4)
        username = "bot{}".format(n)

        b = BotProcess(
            url=url,
            start_event=start_event,
            username=username,
            password=pwd
        )

        b.start()

    # ml.Event().wait(2)

    start_event.set()


if __name__ == "__main__":

    main()
