# from django.test import TestCase
from game.models import User


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

    create_bots(n_bots)


main()
