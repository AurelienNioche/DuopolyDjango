from django.contrib import admin

# Register your models here.
from . models import Users, FirmProfits, FirmPositions, FirmPrices, \
    ConsumerChoices, Players, Room, RoundState, Round, RoundComposition


class UsersAdmin(admin.ModelAdmin):
    list_display = ("username", "player_id", "password", "deserter",
                    "email", "gender", "mechanical_id", "age", "nationality")


class PlayersAdmin(admin.ModelAdmin):
    list_display = \
        ("player_id", "room_id", "state", "last_request", "time_last_request")


class FirmProfitsAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class FirmPositionsAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class FirmPricesAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class ConsumerChoicesAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class RoundAdmin(admin.ModelAdmin):
    list_display = ("round_id", "room_id", "ending_t", "opened", "missing_players",
                    "real_players", "state", "t")


class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_id", "radius", "opened", "missing_players", "trial", "ending_t", "state")


class RoundCompositionAdmin(admin.ModelAdmin):
    list_display = ("round_id", "player_id", "agent_id", "bot", "role")


class RoundStateAdmin(admin.ModelAdmin):
    list_display = ("round_id", "t", "firm_active", "firm_active_played", "consumers_played")


admin.site.register(Room, RoomAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(RoundComposition, RoundCompositionAdmin)
admin.site.register(RoundState, RoundStateAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(Players, PlayersAdmin)
admin.site.register(FirmProfits, FirmProfitsAdmin)
admin.site.register(FirmPositions, FirmPositionsAdmin)
admin.site.register(FirmPrices, FirmPricesAdmin)
admin.site.register(ConsumerChoices, ConsumerChoicesAdmin)
