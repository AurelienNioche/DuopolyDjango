from django.contrib import admin

# Register your models here.
from . models import IntParameter


class IntParameterAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "unit")


admin.site.register(IntParameter, IntParameterAdmin)
