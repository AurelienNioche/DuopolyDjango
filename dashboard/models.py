from django.db import models


class IntParameter(models.Model):

    name = models.TextField()
    value = models.IntegerField()
    unit = models.TextField()

    class Meta:
        verbose_name_plural = "IntParameters"

