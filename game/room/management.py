import os
import secrets
from utils import utils

from game.models import Room, Users, Players


from game import round

from . import composition, state

__path__ = os.path.relpath(__file__)


def create(data):

    is_trial = int(bool(data['trial']))
    ending_t = int(data["ending_t"])
    radius = data['radius']

    missing_players = 1 if is_trial else 2

    # get room_id: if already exists, increment
    # until it doesnt found an existing record
    room_id = 1

    while True:

        if Room.objects.filter(room_id=room_id).first() is None:
            break

        else:
            room_id += 1

    round.dialog.create_rounds(
        room_id=room_id, ending_t=ending_t, trial=is_trial,
        called_from=__path__ + "." + utils.fname()
    )

    rm = Room(
        state=state.tutorial,
        ending_t=ending_t,
        radius=radius,
        player_0=_generate_unique_player_id(),
        player_1=_generate_unique_player_id(),
        trial=is_trial,
        missing_players=missing_players,
        room_id=room_id,
        opened=1
    )

    rm.save()


def delete(room_id):

    """
    Get room and compositions related then delete
    :param room_id:
    :return:
    """

    entry = Room.objects.filter(room_id=room_id).first()
    if entry is not None:
        entry.delete()

    entries = Players.objects.filter(room_id=room_id)
    if entries.count():
        entries.delete()

    round.dialog.delete_rounds(room_id=room_id, called_from=__path__+":"+utils.fname())


def close(room_id):

    entry = Room.objects.get(room_id=room_id)
    entry.opened = 0
    entry.save(force_update=True)
    utils.log("The room {} is now closed.".format(room_id), f=utils.fname(), path=__path__)


def get_list():

    class ConnectedPlayer:
        def __init__(self, username, deserter, p_state, last_request, time_last_request):
            self.username = username
            self.deserter = deserter
            self.state = p_state
            self.last_request = last_request
            self.time_last_request = time_last_request

    rooms = Room.objects.all().order_by("room_id")
    rooms_list = []

    for room in rooms:

        players = composition.get_connected_players(room_id=room.room_id)
        connected_players = []

        for p in players:

            user = Users.objects.filter(player_id=p.player_id).first()
            cp = ConnectedPlayer(
                username=user.username,
                deserter=user.deserter,
                p_state=p.state,
                last_request=p.last_request,
                time_last_request=p.time_last_request
            )
            connected_players.append(cp)

        dic = {"att": room, "connected_players": connected_players}
        rooms_list.append(dic)

    return rooms_list


def _generate_unique_player_id():

    player_id = secrets.token_hex(10)

    while True:

        cond0 = Room.objects.filter(player_0=player_id).first() is not None
        cond1 = Room.objects.filter(player_1=player_id).first() is not None

        if cond0 or cond1:
            player_id = secrets.token_hex(10)
        else:
            return player_id

