# from django.test import TestCase
from game.models import User, Room


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


def main():

    n_bots = 40

    delete_bots()
    create_bots(n_bots)


def get_rooms():
    rooms_025 = Room.objects.filter(opened=True, missing_players=2, radius=0.25)
    rooms_05 = Room.objects.filter(opened=True, missing_players=2, radius=0.5)

    print("N opened room 025:", rooms_025.count())
    print("N opened room 05:", rooms_05.count())


get_rooms()

