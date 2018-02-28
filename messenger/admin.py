from django.contrib import admin

from . models import Message, BoolParameter


class MessageAdmin(admin.ModelAdmin):

    list_display = \
        ("author", "to", "message", "time_stamp", "receipt_confirmation")


class BoolParameterAdmin(admin.ModelAdmin):

    list_display = \
        ("name", "value")


admin.site.register(Message, MessageAdmin)
admin.site.register(BoolParameter, BoolParameterAdmin)