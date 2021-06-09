from datetime import date, datetime, timedelta
from dateutil import relativedelta
from dateutil.rrule import rrule
from django.test import TestCase
from events.models import (Event,
                          EventClone,
                          get_occurrences,
                          next_month)
from test_api import datetimestr


class Test(TestCase):

    def setUp(self):
        Event.objects.create(**{
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 1,
            'date': '2021-07-21',
            'periodicity': 'weekly',
        })

    def test_get_occurences(self):
        e = Event.objects.get(id=1)
        first = date(2021, 8, 4)
        until = e.date + relativedelta.relativedelta(months=2)
        month = next_month(e.date.month)
        rrule_bymonth = [month, next_month(month)]
        expected = [
            EventClone(e, date=first),
            EventClone(e, date=first + timedelta(days=7)),
            EventClone(e, date=first + timedelta(days=14)),
            EventClone(e, date=first + timedelta(days=21)),
            EventClone(e, date=first + timedelta(days=28)),
            EventClone(e, date=first + timedelta(days=35)),
            EventClone(e, date=first + timedelta(days=42)),
        ]
        self.assertEqual(get_occurrences(e, e.date, until, rrule_bymonth), expected)
