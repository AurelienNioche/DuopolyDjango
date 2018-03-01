from django.db.models import Q
import os

from messenger.models import Message, BoolParameter

from game.models import User, Round
import game.room.state

from utils import utils
from parameters import parameters

__path__ = os.path.relpath(__file__)


def get_all_messages_from_user(user):
    return Message.objects.filter(Q(author=user, to="admin") | Q(author="admin", to=user)).order_by('id')


def get_all_users():

    users = User.objects.all().order_by("registered", "room_id", "username")
    user_list = []

    # We sort users by room ids
    for u in users:

        if u.registered:

            # set progression
            if u.state == game.room.state.tutorial:
                progression = round(u.tutorial_progression)
                u.progression = progression if progression != -1 else 0

            elif u.state == game.room.state.pve or u.state == game.room.state.pvp:
                rd = Round.objects.get(id=u.round_id)
                u.progression = round((rd.t / rd.ending_t) * 100)

        else:

            u.state = None
            u.progression = None
            u.room_id = None

        u.n_unread = get_unread_msg(u.username)
        user_list.append(u)

    return user_list


def get_user_from_id(user_id):
    return User.objects.get(id=user_id).username


def set_user_msg_as_read(username):

    entries = Message.objects.filter(author=username)

    for e in entries:
        e.receipt_confirmation = True
        e.save(update_fields=["receipt_confirmation"])


def get_unread_msg(username=None):

    if username is not None:
        unread = Message.objects.filter(author=username, receipt_confirmation=False).count()
    else:
        unread = Message.objects.filter(receipt_confirmation=False).exclude(author="admin").count()
    return unread


def send_message(username, message):

    new_entry = Message(
        author="admin",
        to=username,
        message=message,
        receipt_confirmation=True
    )

    new_entry.save()


def get_messages_for_client(username):

    entries = Message.objects.filter(author="admin", to=username, receipt_confirmation=False)
    n_new_messages = len(entries)
    new_messages = [i.message for i in entries]

    return n_new_messages, new_messages


def new_message_from_client(cls, username, message):

    new_entry = Message(
        author=username,
        to="admin",
        message=message,
        receipt_confirmation=False,
    )

    new_entry.save()

    cls.send_auto_reply(username)


def receipt_confirmation_from_client(username, messages):

    for msg in messages:
        entry = Message.objects.filter(author="admin", to=username, message=msg, receipt_confirmation=False).first()
        entry.receipt_confirmation = True
        entry.save(update_fields=["receipt_confirmation"])


def send_auto_reply(cls, username):

    auto_reply = BoolParameter.objects.filter(name="auto_reply").first()

    if auto_reply.value:
        cls.send_message(
            username=username,
            message=parameters.auto_reply_msg.format(utils.get_time_in_france())
        )


def set_auto_reply(value):

    auto_reply = BoolParameter.objects.filter(name="auto_reply").first()

    if int(auto_reply.value) != int(value):
        auto_reply.value = str(value)
        auto_reply.save(update_fields=["value"])


def get_auto_reply():

    auto_reply = BoolParameter.objects.filter(name="auto_reply").first()

    if not auto_reply:
        auto_reply = BoolParameter(
            name="auto_reply",
            value=False
        )
        auto_reply.save()

    return "checked" if auto_reply.value else "notchecked"


def get_latest_msg_author():

    msg = Message.objects.exclude(author="admin")
    if msg:
        sort_last = msg.latest("time_stamp")
        return sort_last.author
