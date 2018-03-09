from django.db.models import Q
from django.utils import timezone
import datetime
import os

from messenger.models import Message, BoolParameter, DateTimeParameter, IntParameter

from game.models import User, Round
import game.room.state

from utils import utils
from parameters import parameters

__path__ = os.path.relpath(__file__)


def get_all_messages_from_user(user):
    return Message.objects.filter(Q(author=user, to="admin") | Q(author="admin", to=user)).order_by('id')


def get_all_users():

    users = User.objects.order_by("registered", "room_id", "username")\
        .only("id", "tutorial_progression", "state", "registered", "connected", "username", "deserter")
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

    return user_list[::-1]


def get_user_from_id(user_id):
    return User.objects.get(id=user_id).username


def set_user_msg_as_read(username):

    entries = Message.objects.only("author", "receipt_confirmation")

    for e in entries:
        if username == e.author:
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
        receipt_confirmation=False
    )

    new_entry.save()


def get_messages_for_client(username):

    entries = Message.objects.filter(author="admin", to=username, receipt_confirmation=False).only("message")
    n_new_messages = len(entries)
    new_messages = [i.message for i in entries]

    return n_new_messages, new_messages


def new_message_from_client(username, message):

    new_entry = Message(
        author=username,
        to="admin",
        message=message,
        receipt_confirmation=False,
    )

    new_entry.save()

    send_auto_reply(username)


def receipt_confirmation_from_client(username, messages):

    for msg in messages:
        entry = Message.objects.filter(author="admin", to=username, message=msg, receipt_confirmation=False).first()
        entry.receipt_confirmation = True
        entry.time_stamp = timezone.now()
        entry.save(update_fields=["receipt_confirmation", "time_stamp"])


def send_auto_reply(username):

    auto_reply = BoolParameter.objects.filter(name="auto_reply").first()

    time_in_france = timezone.now().strftime("%I:%M %p")

    if auto_reply.value:
        send_message(
            username=username,
            message=parameters.auto_reply_msg.format(time_in_france)
        )


def set_auto_reply(value):

    auto_reply = BoolParameter.objects.filter(name="auto_reply").first()

    if auto_reply.value != value:
        utils.log("Auto_reply: {}".format(value), f=set_auto_reply)
        auto_reply.value = value
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
        return User.objects.get(username=sort_last.author)


def has_to_refresh():

    # Get reference time
    reference_time = DateTimeParameter.objects.filter(name="time_last_refresh").first().value

    if reference_time:

        # Then get the timezone
        tz_info = reference_time.tzinfo
        # Get time now using timezone info
        t_now = datetime.datetime.now(tz_info)
        # Generate a timedelta
        param = IntParameter.objects.filter(name="refresh_frequency").first()

        if param is None:
                param = IntParameter(name="refresh_frequency", value=500, unit="milliseconds")
                param.save()

        if param.unit == "seconds":
            delta = datetime.timedelta(seconds=param.value)
        elif param.unit == "milliseconds":
            delta = datetime.timedelta(milliseconds=param.value)
        else:
            delta = datetime.timedelta(minutes=param.value)

        # If more than X min/seconds since the last request
        timeout = t_now > reference_time + delta

        return timeout


def set_time_last_refresh():

    time_last_refresh = DateTimeParameter.objects.filter(name="time_last_refresh").first()

    if time_last_refresh:
        time_last_refresh.value = timezone.now()
        time_last_refresh.save(update_fields=["value"])
    else:
        time_last_refresh = DateTimeParameter(
            name="time_last_refresh",
            value=timezone.now()
        )
        time_last_refresh.save()
