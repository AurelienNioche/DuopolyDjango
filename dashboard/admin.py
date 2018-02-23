from django.contrib import admin

# Register your models here.
from . models import Parameters


class ParametersAdmin(admin.ModelAdmin):
    list_display = ("name", "value")


admin.site.register(Parameters, ParametersAdmin)
