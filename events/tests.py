from datetime import datetime
from dateutil import tz, relativedelta
from django.test import TestCase
from events.models import get_occurrences, Event, EventClone
from test_api import shift_from_now


class Test(TestCase):

    def setUp(self):
        Event.objects.create(**{
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 1,
            'date': shift_from_now(-10),
            'periodicity': 'weekly',
        })

    def test_get_occurences(self):
        e = Event.objects.get(id=1)
        until = datetime.now(tz.UTC) + relativedelta.relativedelta(months=1)
        expected = [
            EventClone(e, date=shift_from_now(4)),
            EventClone(e, date=shift_from_now(11)),
            EventClone(e, date=shift_from_now(18)),
            EventClone(e, date=shift_from_now(25)),
        ]
        self.assertEqual(get_occurrences(e, until), expected)
