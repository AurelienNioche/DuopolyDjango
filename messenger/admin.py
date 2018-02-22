from django.db.models import Q
import os

from messenger.models import Messages, MessagesParameters

from game.models import Users, Players, Round
from game import room

from utils import utils
from parameters import parameters


__path__ = os.path.relpath(__file__)


class Admin:

    @classmethod
    def get_all_messages_from_user(cls, user):
        return Messages.objects.filter(Q(author=user, to="admin") | Q(author="admin", to=user)).order_by('id')

    @classmethod
    def get_all_users(cls):

        users = Users.objects.all().order_by("username")

        for u in users:

            player = Players.objects.filter(player_id=u.player_id).first()

            if player is not None:

                u.state = player.state

                # set progression
                if u.state == room.state.tutorial:
                    progression = round(player.tutorial_progression)
                    u.progression = progression if progression != -1 else 0

                elif u.state == room.state.pve or u.state == room.state.pvp:
                    rd = Round.objects.get(round_id=player.round_id)
                    u.progression = round((rd.t / rd.ending_t) * 100)

                u.room_id = player.room_id

            else:
                u.state = None
                u.progression = None
                u.room_id = None

            u.n_unread = cls.get_unread_msg(u.username)

        return list(u for u in users)

    @classmethod
    def get_user_from_id(cls, user_id):
        return Users.objects.get(id=user_id).username

    @classmethod
    def set_user_msg_as_read(cls, username):

        entries = Messages.objects.filter(author=username)

        for e in entries:
            e.receipt_confirmation = 1
            e.save(force_update=True)

    @classmethod
    def get_unread_msg(cls, username=None):
        if username is not None:
            unread = Messages.objects.filter(author=username, receipt_confirmation=0).count()
        else:
            unread = Messages.objects.filter(receipt_confirmation=0).exclude(author="admin").count()
        return unread

    @classmethod
    def send_message(cls, username, message):

        new_entry = Messages(
            author="admin",
            to=username,
            message=message,
            receipt_confirmation=0
        )

        new_entry.save()

    @classmethod
    def get_messages_for_client(cls, username):

        entries = Messages.objects.filter(author="admin", to=username, receipt_confirmation=0)
        n_new_messages = len(entries)
        new_messages = [i.message for i in entries]
        return n_new_messages, new_messages

    @classmethod
    def new_message_from_client(cls, username, message):

        new_entry = Messages(author=username, to="admin", message=message, receipt_confirmation=0)
        new_entry.save()

        cls.send_auto_reply(username)

    @classmethod
    def receipt_confirmation_from_client(cls, username, messages):

        for msg in messages:
            entry = Messages.objects.filter(author="admin", to=username, message=msg, receipt_confirmation=0).first()
            entry.receipt_confirmation = 1
            entry.save()

    @classmethod
    def send_auto_reply(cls, username):

        auto_reply = MessagesParameters.objects.filter(name="auto_reply").first()

        if int(auto_reply.value):

            # Import here in order to refresh hour
            from parameters import parameters
            cls.send_message(
                    username=username,
                    message=parameters.auto_reply_msg.format(utils.get_time_in_france())
            )

    @classmethod
    def set_auto_reply(cls, value):

        auto_reply = MessagesParameters.objects.filter(name="auto_reply").first()

        if int(auto_reply.value) != int(value):
            auto_reply.value = str(value)
            auto_reply.save(force_update=True)

    @classmethod
    def get_auto_reply(cls):

        auto_reply = MessagesParameters.objects.filter(name="auto_reply").first()

        if not auto_reply:
            auto_reply = MessagesParameters(
                name="auto_reply",
                value=str(0)
            )
            auto_reply.save()

        return "checked" if  int(auto_reply.value) else "notchecked"
