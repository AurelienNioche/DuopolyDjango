from django.contrib import admin

# Register your models here.
from . models import User, FirmProfit, FirmPosition, FirmPrice, \
    ConsumerChoice, Room, RoundState, Round, RoundComposition, RoomComposition


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "password", "email", "gender", "mechanical_id", "age", "nationality",
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
        "id", "room_id", "pvp", "missing_players", "ending_t", "t", "radius")


class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "id", "opened", "missing_players", "trial", "radius",
        "ending_t", "state")


class RoomCompositionAdmin(admin.ModelAdmin):
    list_display = (
        "room_id", "user_id", "available"
    )


class RoundCompositionAdmin(admin.ModelAdmin):
    list_display = ("round_id", "user_id", "firm_id", "bot", "available")


class RoundStateAdmin(admin.ModelAdmin):
    list_display = ("round_id", "t", "firm_active", "firm_active_and_consumers_played")


admin.site.register(Room, RoomAdmin)
admin.site.register(RoomComposition, RoomCompositionAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(RoundComposition, RoundCompositionAdmin)
admin.site.register(RoundState, RoundStateAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(FirmProfit, FirmProfitAdmin)
admin.site.register(FirmPosition, FirmPositionAdmin)
admin.site.register(FirmPrice, FirmPriceAdmin)
admin.site.register(ConsumerChoice, ConsumerChoiceAdmin)
