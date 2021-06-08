
import calendar
from datetime import datetime, timedelta
from dateutil import tz
from rest_framework.test import APITestCase
from rest_framework import status
from events.models import User, Event


class EventTests(APITestCase):

    def setUp(self):
        u = User.objects.create(username='Steven')
        u.set_password('Jobs')
        u.save()

    def test_add_event(self):
        self.client.login(username='Steven', password='Jobs')
        date = datetime.today() + timedelta(days=1)
        events_data = [
            {'title': 'Title1', 'city': 'City1', 'cost': 500,
             'tickets': 100, 'date': date, 'perodicity': 'one-off'},
            {'title': 'Title2', 'city': 'City2', 'cost': 500,
             'tickets': 100, 'date': date + timedelta(days=3), 'periodicity': 'weekly'},
            {'title': 'Title3', 'city': 'City3', 'cost': 500,
             'tickets': 100, 'date': date + timedelta(days=20), 'periodicity': 'monthly'},
            {'title': 'Title4', 'city': 'City3', 'cost': 500,
             'tickets': 100, 'date': date + timedelta(days=1), 'periodicity': 'yearly'},
            {'title': 'Title5', 'city': 'City3', 'cost': 500,
             'tickets': 3, 'date': date + timedelta(days=10), 'periodicity': 'weekly'},
        ]
        for data in events_data:
            response = self.client.post('/event', data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response)

    def test_get_upcoming(self):
        # prepare data
        days_delta = -5
        ev_data = {
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 100,
            'date': datetimestr(days_delta),
            'periodicity': 'weekly'
        }
        Event.objects.create(**ev_data)
        expected = [
            {**ev_data, 'date': datetimestr(days_delta + 7)},
            {**ev_data, 'date': datetimestr(days_delta + 14)},
            {**ev_data, 'date': datetimestr(days_delta + 21)},
            {**ev_data, 'date': datetimestr(days_delta + 28)},
            {**ev_data, 'date': datetimestr(days_delta + 35)},
        ]
        _ = [e.pop('periodicity') for e in expected]
        response = self.client.get('/get-events/upcoming?city=City3')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        msg=f'{response.json()}\n{expected}'
        self.assertEqual(response.json(), expected, msg=msg)

    def test_get_month(self):
        # prepare data
        days_delta = -5
        ev_data = {
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 100,
            'date': datetimestr(days_delta),
            'periodicity': 'weekly'
        }
        ev1_data = {
            'title': 'Title5',
            'city': 'City3',
            'cost': 500,
            'tickets': 100,
            'date': datetimestr(10),
            'periodicity': 'one-off'
        }
        Event.objects.create(**ev_data)
        Event.objects.create(**ev1_data)
        cur_month = calendar.month_abbr[datetime.now().month]
        expected = sorted([
            {**ev_data, 'date': datetimestr(days_delta + 7)},
            {**ev_data, 'date': datetimestr(days_delta + 14)},
            {**ev_data, 'date': datetimestr(days_delta + 21)},
            ev1_data,
        ], key=lambda d: d['date'])
        _ = [e.pop('periodicity') for e in expected]

        response = self.client.get(f'/get-events/month?month={cur_month}')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        data = response.data
        data.sort(key=lambda d: d['date'])
        self.assertEqual(data, expected)

    def test_payment(self):
        # prepare data
        self.client.login(username='Steven', password='Jobs')
        ev_data = {
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 1,
            'date': datetimestr(3),
            'periodicity': 'weekly',
            'id': 10
        }
        Event.objects.create(**ev_data)

        # check payment
        response = self.client.post('/buy-ticket', data={'user_id': 1, 'event': 10, 'transaction_id': 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # check tickets number changed
        expected = ev_data
        expected['tickets'] -= 1
        response = self.client.get('/event/10')
        self.assertEqual(response.json(), ev_data)
        # get no-tickets response
        response = self.client.post('/buy-ticket', data={'user_id': 1, 'event': 10, 'transaction_id': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)


def datetimestr(days_delta=0):
    date = shift_from_now(days_delta)
    return datetime.strftime(date, '%Y-%m-%dT%H:%M:%SZ')


def shift_from_now(days):
    res = datetime.now(tz.UTC) + timedelta(days=days)
    return res.replace(microsecond=0)
