from game.models import Players


def get_connected_players(room_id):

    entries = Players.objects.filter(room_id=room_id)

    return entries
