from django.db import models


class Messages(models.Model):

    author = models.TextField(max_length=30, default="null")
    to = models.TextField(max_length=30, default="null")
    message = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True, blank=True)
    receipt_confirmation = models.IntegerField(default=-1)


class MessagesParameters(models.Model):

    name = models.TextField()
    value = models.TextField()


