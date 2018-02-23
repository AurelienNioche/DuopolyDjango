from django.contrib import admin

# Register your models here.
from . models import IntParameters


class IntParametersAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "unit")


admin.site.register(IntParameters, IntParametersAdmin)
