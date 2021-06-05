from django.db import models
from swingtime import models as stmodels


class Event(stmodels.Event):
    city = models.CharField(max_length=60)
    tickets = models.IntegerField()
    cost = models.FloatField()
    date_time = models.DateTimeField()
    periodicity = models.CharField(max_length=10, choices = (
        ('yearly', 'yearly'),
        ('monthly', 'monthly'),
        ('weekly', 'weekly'),
        ('daily', 'daily'),
    ))
