from django.db import models


class Room(models.Model):

    opened = models.BooleanField(default=False)
    missing_players = models.IntegerField(default=-1)
    user_id_0 = models.IntegerField(default=-1)
    user_id_1 = models.IntegerField(default=-1)
    radius = models.FloatField(default=-1)
    trial = models.BooleanField(default=False)
    ending_t = models.IntegerField(default=-1)
    state = models.TextField(max_length=30, default="null")


class Round(models.Model):

    room_id = models.IntegerField(default=-1)
    missing_players = models.IntegerField(default=-1)
    real_players = models.IntegerField(default=-1)
    state = models.TextField(max_length=30, default="null")
    ending_t = models.IntegerField(default=20)
    radius = models.IntegerField(default=20)
    t = models.IntegerField(default=0)


class RoundComposition(models.Model):

    round_id = models.IntegerField(default=-1)
    user_id = models.IntegerField(default=-1)
    firm_id = models.IntegerField(default=-1)
    bot = models.BooleanField(default=False)


class RoundState(models.Model):

    round_id = models.IntegerField(default=-1)
    t = models.IntegerField(default=-1)
    firm_active_played = models.IntegerField(default=-1)
    firm_active = models.IntegerField(default=-1)
    consumers_played = models.IntegerField(default=-1)


class User(models.Model):

    username = models.TextField(max_length=30, default="null", unique=True)
    password = models.TextField(max_length=30, default="null")
    email = models.TextField(max_length=30, default="null")
    gender = models.TextField(max_length=30, default="null")
    mechanical_id = models.TextField(max_length=30, default="null")
    age = models.IntegerField(default=-1)
    nationality = models.TextField(max_length=30, default="null")
    deserter = models.IntegerField(default=0)
    time_last_request = models.DateTimeField(auto_now_add=True, blank=True)
    last_request = models.TextField(max_length=50, default="null")
    connected = models.IntegerField(default=0)
    registered = models.IntegerField(default=-1)
    registration_time = models.DateTimeField(auto_now_add=True, blank=True)
    state = models.TextField(max_length=30, default="null")
    tutorial_progression = models.FloatField(default=0)
    room_id = models.IntegerField(default=-1)
    round_id = models.IntegerField(default=-1)
    firm_id = models.IntegerField(default=-1)


class Data(models.Model):

    round_id = models.IntegerField(default=-1)
    agent_id = models.IntegerField(default=-1)
    t = models.IntegerField(default=-1)
    value = models.IntegerField(default=-1)

    class Meta:
        abstract = True


class FirmProfit(Data):

    class Meta:
        pass


class FirmProfitPerTurn(Data):

    class Meta:
        pass


class FirmPrice(Data):

    class Meta:
        pass


class FirmPosition(Data):

    class Meta:
        pass


class ConsumerChoice(Data):

    class Meta:
        pass
