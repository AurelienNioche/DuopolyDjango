from game.models import User

from . import management


def check_connected_users():
    users = User.objects.all()
    management.check_connected_users(users=users)
