from django.db import models


class Room(models.Model):

    room_id = models.IntegerField(default=-1, unique=True)
    opened = models.IntegerField(default=-1)
    missing_players = models.IntegerField(default=-1)
    player_0 = models.TextField(default="null", unique=True)
    player_1 = models.TextField(default="null", unique=True)
    radius = models.FloatField(default=-1)
    trial = models.IntegerField(default=-1)
    ending_t = models.IntegerField(default=-1)
    state = models.TextField(max_length=30, default="null")


class Round(models.Model):

    round_id = models.TextField(max_length=20, default="null", unique=True)
    room_id = models.IntegerField(default=-1)
    opened = models.IntegerField(default=-1)
    missing_players = models.IntegerField(default=-1)
    real_players = models.IntegerField(default=-1)
    state = models.TextField(max_length=30, default="null")
    ending_t = models.IntegerField(default=20)
    t = models.IntegerField(default=0)


class RoundComposition(models.Model):

    round_id = models.TextField(max_length=20, default="null")
    player_id = models.TextField(max_length=20, default="null")
    agent_id = models.IntegerField(default=-1)
    role = models.TextField(max_length=30, default="null")
    bot = models.IntegerField(default=-1)


class RoundState(models.Model):

    round_id = models.TextField(max_length=20, default="null")
    t = models.IntegerField(default=-1)
    firm_active_played = models.IntegerField(default=-1)
    firm_active = models.IntegerField(default=-1)
    consumers_played = models.IntegerField(default=-1)


class Players(models.Model):

    class Meta:
        verbose_name_plural = "players"

    player_id = models.TextField(max_length=20, default="null", unique=True)
    room_id = models.IntegerField(default=-1)
    round_id = models.TextField(max_length=20, default="null")
    time_last_request = models.DateTimeField(auto_now_add=True, blank=True)
    last_request = models.TextField(max_length=30, default="null")
    state = models.TextField(max_length=30, default="null")
    tutorial_progression = models.FloatField(default=0)


class Users(models.Model):

    class Meta:
        verbose_name_plural = "users"

    username = models.TextField(max_length=30, default="null", unique=True)
    player_id = models.TextField(max_length=20, default="null")
    password = models.TextField(max_length=30, default="null")
    email = models.TextField(max_length=30, default="null")
    gender = models.TextField(max_length=30, default="null")
    mechanical_id = models.TextField(max_length=30, default="null")
    age = models.IntegerField(default=-1)
    nationality = models.TextField(max_length=30, default="null")
    deserter = models.IntegerField(default=0)


class Data(models.Model):

    round_id = models.TextField(max_length=20, default="null")
    agent_id = models.IntegerField(default=-1)
    t = models.IntegerField(default=-1)
    value = models.IntegerField(default=-1)

    class Meta:
        abstract = True


class FirmProfits(Data):

    class Meta:
        verbose_name_plural = "firmProfits"


class FirmProfitsPerTurn(Data):

    class Meta:
        verbose_name_plural = "firmProfitsPerTurn"


class FirmPrices(Data):

    class Meta:
        verbose_name_plural = "firmPrices"


class FirmPositions(Data):

    class Meta:
        verbose_name_plural = "firmPositions"


class ConsumerChoices(Data):

    class Meta:
        verbose_name_plural = "consumerChoices"
