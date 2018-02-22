from game.models import Players


def get_tutorial_progression(player_id):
    tutorial_progression = Players.objects.get(player_id=player_id).tutorial_progression
    return tutorial_progression
