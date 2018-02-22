from . import management


def set_time_last_request(player_id, function_name):
    """
    called from game.views
    """
    management.set_time_last_request(player_id=player_id, function_name=function_name)
