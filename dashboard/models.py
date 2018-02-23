from django.db import models


class IntParameters(models.Model):

    name = models.TextField()
    value = models.IntegerField()
    unit = models.TextField()

    class Meta:
        verbose_name_plural = "IntParameters"

