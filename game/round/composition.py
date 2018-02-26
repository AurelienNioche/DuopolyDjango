import os
import numpy as np

from utils import utils
from parameters import parameters

from game.models import RoundComposition, Round

from game import room


__path__ = os.path.relpath(__file__)


def create(round_id, n_real_players):

    # create composition
    roles = np.array(['firm', ] * parameters.n_firms + ['consumer', ] * parameters.n_consumers)
    n_player = len(roles)
    bots = np.ones(n_player)

    bots[:n_real_players] = 0

    for i in range(n_player):
        composition = RoundComposition(
            round_id=round_id,
            agent_id=i,
            role=roles[i],
            bot=int(bots[i])
        )

        composition.save()


def delete(round_id):

    utils.log("Delete composition corresponding to 'round_id' '{}'".format(round_id),
              path=__path__, f=utils.fname())

    rc = RoundComposition.objects.filter(round_id=round_id)
    if rc.count():
        rc.delete()


def include_players_into_round_compositions(room_id, player_id):

    rd_pve = Round.objects.filter(room_id=room_id, state=room.state.pve).exclude(missing_players=0).first()
    rd_pvp = Round.objects.filter(room_id=room_id, state=room.state.pvp).exclude(missing_players=0).first()

    rd_pve.missing_players -= 1
    rd_pvp.missing_players -= 1

    # If round pve does not welcome additional players
    if rd_pve.missing_players == 0:
        rd_pve.opened = 0

    # If round pvp does not welcome additional players
    if rd_pvp.missing_players == 0:
        rd_pvp.opened = 0

    rd_pve.save()
    rd_pvp.save()

    # set player to agent_id firm 0 in round pve
    agent_id = 0
    rc_pve = RoundComposition.objects.filter(round_id=rd_pve.round_id, agent_id=agent_id).first()
    rc_pve.player_id = player_id

    agent_id = rd_pvp.missing_players  # Since already decreased, it will be either 0 or 1
    rc_pvp = RoundComposition.objects.filter(round_id=rd_pvp.round_id, agent_id=agent_id).first()
    rc_pvp.player_id = player_id

    rc_pve.save()
    rc_pvp.save()

    return rd_pve.round_id
