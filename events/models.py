
import datetime
from dateutil import rrule, relativedelta, tz
from django.db import models


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
    def get_month_occurrences(cls, month):
        print(month)
        earliest = datetime.datetime.now(tz.UTC).replace(month=month, day=1)
        print(earliest)
        until = earliest + relativedelta.relativedelta(months=1)
        objects = []
        for o in cls.objects.filter(date__gte=earliest, tickets__gt=0):
            if o.periodicity != 'one-off':
                objects.extend(get_occurrences(o.date, until, o.periodicity, o))
            else:
                objects.append(o)
        return objects

    @classmethod
    def get_upcoming_occurences(cls, city):
        earliest = datetime.datetime.now(tz.UTC)
        until = earliest + relativedelta.relativedelta(months=1)
        objects = []
        for o in cls.objects.filter(date__gte=earliest, city=city, tickets__gt=0):
            if o.periodicity != 'one-off':
                objects.extend(get_occurrences(o.date, until, o.periodicity, o))
            else:
                objects.append(o)
        return objects


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


def get_occurrences(date, until, freq, event):
    # retrive rrule corresponding freq value
    rrule_freq = getattr(rrule, freq.upper())
    # cast datetimes via rrule
    occur = list(rrule.rrule(rrule_freq, dtstart=date, until=until))
    return [EventClone(event, date=dt) for dt in occur]
