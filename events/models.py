

import datetime
from dateutil import rrule, relativedelta, tz
from django.core.exceptions import ObjectDoesNotExist
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
        until -= datetime.timedelta(days=1)
        kwargs = {'title': title} if title else {}
        objects = list(cls.objects.filter(date__gte=earliest,
                                          periodicity='one-off',
                                          **kwargs))
        periodic = list(
            cls.objects.exclude(periodicity='one-off').filter(**kwargs)
        )
        periodic = cls.init_periodic_tickets(periodic)
        for o in periodic:
            objects += get_occurrences(o, until)
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
        periodic = cls.init_periodic_tickets(periodic)
        for o in periodic:
            objects += get_occurrences(o, until)
        return objects

    @classmethod
    def init_periodic_tickets(cls, objects):
        dates = tuple(o.date for o in objects)
        print('dates', dates)
        query = TicketsLeft.objects.filter(date__in=dates)
        tickets_by_dates = {tickets.date: tickets for tickets in query}
        print('by dates', tickets_by_dates)
        for o in objects:
            tickets = tickets_by_dates.get(o.date)
            if tickets is not None:
                o.date = tickets.date
        return objects

class TicketsLeft(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    tickets = models.IntegerField()
    date = models.DateTimeField()


class Payment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    transaction_id = models.IntegerField(null=False, blank=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.RESTRICT)
    cost = models.FloatField()

    def save(self, date, *args, **kwargs):
        if self.event.periodicity != 'one-off':
            try:
                tickets = TicketsLeft.objects.get(event=self.event, date=date)
                if tickets.tickets <= 0:
                    raise ValidationError('error: no tickets for this event')
                tickets.tickets -= 1
                tickets.date = date
                tickets.save()
            except ObjectDoesNotExist:
                tickets = TicketsLeft(event=self.event, date=date, tickets=self.event.tickets-1)
                tickets.save()

        else:
            if self.event.tickets <= 0:
                raise ValidationError('error: no tickets for this event')
            self.event.tickets -= 1
            self.event.save()

        self.cost = self.event.cost
        super().save(*args, **kwargs)


class EventClone:
    '''simple Event object simulation
    used to cast event occurences'''

    fields = ['title', 'city', 'cost', 'tickets', 'id', ]

    def __init__(self, event, **attrs):
        self.event_object = event
        for attr in self.fields:
            val = getattr(event, attr)
            setattr(self, attr, val)
        for attr, val in attrs.items():
            setattr(self, attr, val)
    
    def __eq__(self, other):
        to_compare = self.fields + ['date']
        for attr in to_compare:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True


def get_occurrences(event, until):
    freq = event.periodicity
    now = datetime.datetime.now(tz.UTC)
    curmonth = now.month
    nextmonth = (curmonth + 1) * (curmonth <= 12)
    # limit rrule occurences
    months = [curmonth, nextmonth]
    # retrive rrule corresponding freq value
    rrule_freq = getattr(rrule, freq.upper())
    # cast datetimes via rrule
    occur = list(rrule.rrule(rrule_freq, dtstart=event.date, until=until, bymonth=months))
    return [EventClone(event, date=dt) for dt in occur if dt >= now]
