from django.db import models


class Room(models.Model):

    opened = models.BooleanField(default=False)
    missing_players = models.IntegerField(default=-1)
    radius = models.FloatField(default=-1)
    trial = models.BooleanField(default=False)
    ending_t = models.IntegerField(default=-1)
    state = models.TextField(max_length=30, default="null")


class RoomComposition(models.Model):

    room_id = models.IntegerField(db_index=True, default=-1)
    user_id = models.IntegerField(default=-1)
    available = models.BooleanField(default=True)


class Round(models.Model):

    room_id = models.IntegerField(default=-1)
    pvp = models.BooleanField(default=False)
    missing_players = models.IntegerField(default=-1)
    ending_t = models.IntegerField(default=20)
    radius = models.FloatField(default=-1)
    t = models.IntegerField(default=0)


class RoundComposition(models.Model):

    round_id = models.IntegerField(default=-1)
    user_id = models.IntegerField(default=-1)
    firm_id = models.IntegerField(default=-1)
    bot = models.BooleanField(default=False)
    available = models.BooleanField(default=True)


class RoundState(models.Model):

    round_id = models.IntegerField(default=-1)
    t = models.IntegerField(default=-1)
    firm_active_played = models.IntegerField(default=-1)
    firm_active = models.IntegerField(default=-1)
    consumers_played = models.IntegerField(default=-1)


class User(models.Model):

    username = models.TextField(db_index=True, max_length=40, unique=True)
    password = models.TextField(max_length=4, default=None)
    email = models.TextField(max_length=40, default=None, null=True)
    gender = models.TextField(max_length=6, default=None, null=True)
    mechanical_id = models.TextField(max_length=30, default=None, null=True)
    age = models.IntegerField(default=-1, null=True)
    nationality = models.TextField(max_length=40, default=None, null=True)
    deserter = models.BooleanField(default=False)
    time_last_request = models.DateTimeField(auto_now_add=True, blank=True)
    last_request = models.TextField(max_length=40, default=None, null=True)
    connected = models.BooleanField(default=False)
    registered = models.BooleanField(default=False)
    registration_time = models.DateTimeField(auto_now_add=True, blank=True)
    state = models.TextField(max_length=30, default=None, null=True)
    tutorial_progression = models.FloatField(default=0, null=True)
    room_id = models.IntegerField(default=-1, null=True)
    round_id = models.IntegerField(default=-1, null=True)
    firm_id = models.IntegerField(default=-1, null=True)


class Data(models.Model):

    round_id = models.IntegerField(default=-1)
    agent_id = models.IntegerField(default=-1)
    t = models.IntegerField(default=-1)
    value = models.IntegerField(default=-1)

    class Meta:
        abstract = True


class FirmProfit(Data):
    pass


class FirmPrice(Data):
    pass


class FirmPosition(Data):
    pass


class ConsumerChoice(Data):
    pass
