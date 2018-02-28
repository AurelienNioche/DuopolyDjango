from game.models import Room

none = "none"
tutorial = "tutorial"
pve = "pve"
pvp = "pvp"
end = "end"


# def update(room_id, state):
#
#     rm = Room.objects.get(room_id=room_id)
#     rm.state = state
#     rm.save()


def get(room_id):

    rm = Room.objects.get(room_id=room_id)
    return rm.state
