

import datetime
from dateutil import rrule, relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError as RestValidationError

User = get_user_model()


class Event(models.Model):
    title = models.CharField(max_length=200)
    city = models.CharField(max_length=60)
    tickets = models.IntegerField()
    cost = models.FloatField()
    # serves as a starting point for periodic events
    date = models.DateField()
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
        earliest = datetime.date.today().replace(month=month)
        until = earliest + relativedelta.relativedelta(months=1)
        rrule_bymonth = [month]
        kwargs = {'title': title} if title else {}
        
        one_off = list(cls.objects.filter(date__gte=earliest,
                                          date__lte=until,
                                          periodicity='one-off',
                                          **kwargs))
        periodic = list(
            cls.objects.exclude(periodicity='one-off').filter(**kwargs)
        )
        periodic_casted = []
        for o in periodic:
            periodic_casted += get_occurrences(o, o.date,
                                               until,
                                               rrule_bymonth)

        periodic_casted = cls.init_periodic_tickets(periodic_casted)
        return periodic_casted + one_off

    @classmethod
    def get_upcoming_occurences(cls, city):
        now = datetime.date.today()
        until = now + relativedelta.relativedelta(months=1)
        rrule_bymonth = [now.month, next_month(now.month)]

        one_off = list(cls.objects.filter(date__gte=now,
                                          date__lte=until,
                                          city=city,
                                          tickets__gt=0,
                                          periodicity='one-off'))
        periodic = list(
            cls.objects.filter(city=city).exclude(periodicity='one-off')
        )
        periodic_casted = []
        for o in periodic:
            periodic_casted += [o_ for o_ in  get_occurrences(o, o.date,
                                                              until,
                                                              rrule_bymonth)
                                if o_.date >= now]
        periodic_casted = cls.init_periodic_tickets(periodic_casted)
        return periodic_casted + one_off

    @classmethod
    def init_periodic_tickets(cls, objects):
        dates = set(o.date for o in objects)
        events = set(Event.objects.get(id=o.id) for o in objects)
        query = TicketsLeft.objects.filter(date__in=dates, event__in=events)
        tickets_by_dates = {tickets.date: tickets for tickets in query}
        for o in objects:
            tickets = tickets_by_dates.get(o.date)
            if tickets is not None:
                o.tickets = tickets.tickets
        return objects


class TicketsLeft(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    tickets = models.IntegerField()
    date = models.DateField()


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
                    raise RestValidationError('error: no tickets for this event')
                tickets.tickets -= 1
                tickets.date = date
                tickets.save()
            except ObjectDoesNotExist:
                if date != self.event.date:
                    raise RestValidationError('error: wrong event date specified')
                tickets = TicketsLeft(event=self.event, date=date, tickets=self.event.tickets-1)
                tickets.save()

        else:
            if self.event.tickets <= 0:
                raise RestValidationError('error: no tickets for this event')
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


def get_occurrences(event, dtstart, until, bymonth):
    freq = event.periodicity
    # retrive rrule corresponding freq value
    rrule_freq = getattr(rrule, freq.upper())
    # cast datetimes via rrule
    occur = rrule.rrule(rrule_freq, dtstart=dtstart, until=until, bymonth=bymonth)
    return [EventClone(event, date=dt.date()) for dt in occur]


def next_month(month):
    return (month + 1) * (month < 12) + (month >= 12)
