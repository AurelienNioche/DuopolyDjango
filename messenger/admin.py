from django.contrib import admin

from . models import Message, BoolParameter, IntParameter, DateTimeParameter


class MessageAdmin(admin.ModelAdmin):

    list_display = \
        ("author", "to", "message", "time_stamp", "receipt_confirmation")


class BoolParameterAdmin(admin.ModelAdmin):

    list_display = \
        ("name", "value")


class DateTimeParameterAdmin(admin.ModelAdmin):
    list_display = \
        ("name", "value")


class IntParameterAdmin(admin.ModelAdmin):
    list_display = \
        ("name", "value", "unit")


admin.site.register(DateTimeParameter, DateTimeParameterAdmin)
admin.site.register(IntParameter, IntParameterAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(BoolParameter, BoolParameterAdmin)