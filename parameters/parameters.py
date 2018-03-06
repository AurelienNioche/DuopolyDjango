import os


n_consumers = 21
n_firms = 2
n_positions = 21
n_prices = 11


error = {
    "wait": -1,
    "time_is_superior": -2,
    "opponent_quit": -3,
    "player_quit": -4,
    "no_opponent_found": -5,
}


# Where we save logs
logs_path = os.getcwd() + "/log/"


auto_reply_msg = "Hi! Thanks for joining the experiment! Unfortunately we're not available "\
             "for the moment. The team is French and it is currently {} in France. We hope that you'll enjoy (enjoyed)"\
             "the game! If you're looking for the survey code, it's 999. In case of bug, enter the"\
             " code anyway and write us a mail! "
