from . import management


def delete(room_id):
    management.delete(room_id=room_id)


def create(data):
    management.create(data=data)


def get_list():
    return management.get_list()
