from django.contrib import admin

# Register your models here.
from . models import User, FirmProfit, FirmPosition, FirmPrice, \
    ConsumerChoice, Room, RoundState, Round, RoundComposition


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username", "password", "email", "gender", "mechanical_id", "age", "nationality",
        "deserter", "time_last_request", "last_request", "connected", "registered", "registration_time",
        "state", "tutorial_progression", "room_id", "round_id", "firm_id")


class FirmProfitAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class FirmPositionAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class FirmPriceAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class ConsumerChoiceAdmin(admin.ModelAdmin):
    list_display = ("round_id", "agent_id", "t", "value")


class RoundAdmin(admin.ModelAdmin):
    list_display = (
        "room_id", "ending_t", "missing_players", "real_players", "state", "t")


class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "opened", "missing_players", "trial", "radius",
        "ending_t", "state", "user_id_0", "user_id_1")


class RoundCompositionAdmin(admin.ModelAdmin):
    list_display = ("round_id", "user_id", "firm_id", "bot")


class RoundStateAdmin(admin.ModelAdmin):
    list_display = ("round_id", "t", "firm_active", "firm_active_played", "consumers_played")


admin.site.register(Room, RoomAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(RoundComposition, RoundCompositionAdmin)
admin.site.register(RoundState, RoundStateAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(FirmProfit, FirmProfitAdmin)
admin.site.register(FirmPosition, FirmPositionAdmin)
admin.site.register(FirmPrice, FirmPriceAdmin)
admin.site.register(ConsumerChoice, ConsumerChoiceAdmin)
