

import datetime
from dateutil import rrule, relativedelta, tz
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError


User = get_user_model()

class Event(models.Model):
    title = models.CharField(max_length=200)
    city = models.CharField(max_length=60)
    tickets = models.IntegerField()
    cost = models.FloatField()
    # serves as a starting point for periodic events
    date = models.DateTimeField()
    periodicity = models.CharField(
        max_length=10,
        choices=(
            ('yearly', 'yearly'),
            ('monthly', 'monthly'),
            ('weekly', 'weekly'),
            ('daily', 'daily'),
            ('one-off', 'one-off'),
            ),
        default='one-off',
        blank=False)

    @classmethod
    def get_month_occurrences(cls, month, title):
        earliest = datetime.datetime.now(tz.UTC).replace(month=month, day=1)
        until = earliest + relativedelta.relativedelta(months=1)
        objects = list(cls.objects.filter(date__gte=earliest,
                                          title=title,
                                          tickets__gt=0,
                                          periodicity='one-off'))
        periodic = list(
            cls.objects.exclude(periodicity='one-off').filter(title=title, tickets__gt=0)
        )
        for o in periodic:
            objects += get_occurrences(o.date, until, o)
        return objects

    @classmethod
    def get_upcoming_occurences(cls, city):
        earliest = datetime.datetime.now(tz.UTC)
        until = earliest + relativedelta.relativedelta(months=1)
        objects = list(cls.objects.filter(date__gte=earliest,
                                          city=city,
                                          tickets__gt=0,
                                          periodicity='one-off'))
        periodic = list(
            cls.objects.exclude(periodicity='one-off').filter(city=city, tickets__gt=0)
        )
        for o in periodic:
            objects += get_occurrences(o.date, until, o)
        return objects


class Transaction(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    transaction_id = models.IntegerField(null=False, blank=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.RESTRICT)

    def save(self, *args, **kwargs):
        if self.event.tickets <= 0:
            raise ValidationError('error: no tickets for this event')
        self.event.tickets -= 1
        self.event.save()
        super().save(*args, **kwargs)


class EventClone:
    '''simple Event object simulation
    used to cast event occurences'''

    fields = ['title', 'city', 'cost', 'tickets', ]

    def __init__(self, event, **attrs):
        for attr in self.fields:
            val = getattr(event, attr)
            setattr(self, attr, val)
        for attr, val in attrs.items():
            setattr(self, attr, val)


def get_occurrences(date, until, event):
    freq = event.periodicity
    now = datetime.datetime.now(tz.UTC)
    curmonth = now.month
    nextmonth = (curmonth + 1) * (curmonth <= 12)
    # limit rrule occurences
    months = [curmonth, nextmonth]
    # retrive rrule corresponding freq value
    rrule_freq = getattr(rrule, freq.upper())
    # cast datetimes via rrule
    occur = list(rrule.rrule(rrule_freq, dtstart=date, until=until, bymonth=months))
    return [EventClone(event, date=dt) for dt in occur if dt >= now]
