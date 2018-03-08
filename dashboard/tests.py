# from django.test import TestCase
from game.models import User, Room
import sys


def delete_bots():
    users = User.objects.filter(username__startswith="bot")
    users.delete()


def create_bots(n_bots):

    User.objects.bulk_create([
        User(
            username='bot{}'.format(i),
            password='{}'.format(i).zfill(4),
            deserter=False,
            connected=False,
            registered=False
        ) for i in range(n_bots)
    ])


def unblock_players():

    users = User.objects.filter(state="tutorial")

    for u in users:
        room = Room.objects.get(id=u.id)
        if not room.opened:
            room.opened = True
            room.missing_players = 2
            room.save()
            u.registered = False
            u.deserter = False
            u.save()


def reset_bots():

    n_bots = 40

    delete_bots()
    create_bots(n_bots)


def get_rooms():

    rooms_025 = Room.objects.filter(opened=True, missing_players=2, radius=0.25).count()
    rooms_05 = Room.objects.filter(opened=True, missing_players=2, radius=0.5).count()
    rooms_025_done = Room.objects.filter(radius=0.25, state="end").count()
    rooms_05_done = Room.objects.filter(radius=0.5, state="end").count()

    print()
    print("**************************************")
    print("N opened room 025:", rooms_025)
    print("N opened room 05:", rooms_05)
    print("**************************************")
    print("N validated room 025:", rooms_025_done)
    print("N validated room 05:", rooms_05_done)
    print("**************************************")
    print()


unblock_players()
# get_rooms()

