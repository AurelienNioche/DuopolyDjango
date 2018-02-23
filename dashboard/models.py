from django.db import models


class Parameters(models.Model):

    name = models.TextField()
    value = models.FloatField()

    class Meta:
        verbose_name_plural = "IntParameters"

