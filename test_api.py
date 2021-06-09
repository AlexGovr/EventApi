
from datetime import date, timedelta, datetime
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
        dt = date.today() + timedelta(days=1)
        events_data = [
            {'title': 'Title1', 'city': 'City1', 'cost': 500,
             'tickets': 100, 'date': dt, 'perodicity': 'one-off'},
            {'title': 'Title2', 'city': 'City2', 'cost': 500,
             'tickets': 100, 'date': dt + timedelta(days=3), 'periodicity': 'weekly'},
            {'title': 'Title3', 'city': 'City3', 'cost': 500,
             'tickets': 100, 'date': dt + timedelta(days=20), 'periodicity': 'monthly'},
            {'title': 'Title4', 'city': 'City3', 'cost': 500,
             'tickets': 100, 'date': dt + timedelta(days=1), 'periodicity': 'yearly'},
            {'title': 'Title5', 'city': 'City3', 'cost': 500,
             'tickets': 3, 'date': dt + timedelta(days=10), 'periodicity': 'weekly'},
        ]
        for data in events_data:
            response = self.client.post('/event', data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response)

    def test_get_upcoming(self):
        # prepare data
        ev_data = {
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 100,
            'date': date.today(),
            'periodicity': 'weekly',
            'id': 1,
        }
        ev = Event.objects.create(**ev_data)
        dt = ev.date
        expected = [
            {**ev_data, 'date': datetimestr(dt)},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=7))},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=14))},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=21))},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=28))},
        ]
        _ = [e.pop('periodicity') for e in expected]
        response = self.client.get('/get-events/upcoming?city=City3')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        msg=f'{response.json()}\n{expected}'
        self.assertEqual(response.json(), expected, msg=msg)

    def test_get_month(self):
        # prepare data
        year = date.today().year
        ev_data = {
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 100,
            'date': date(year, 7, 3),
            'periodicity': 'weekly',
            'id': 1,
        }
        ev1_data = {
            'title': 'Title5',
            'city': 'City3',
            'cost': 500,
            'tickets': 100,
            'date': date(year, 7, 23),
            'periodicity': 'one-off',
            'id': 2,
        }
        ev = Event.objects.create(**ev_data)
        Event.objects.create(**ev1_data)
        dt = ev.date
        ev1_data['date'] = datetimestr(ev1_data['date'])
        expected = sorted([
            {**ev_data, 'date': datetimestr(dt)},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=7))},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=14))},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=21))},
            {**ev_data, 'date': datetimestr(dt + timedelta(days=28))},
            ev1_data,
        ], key=lambda d: d['date'])
        _ = [e.pop('periodicity') for e in expected]

        response = self.client.get(f'/get-events/month?month=jul')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        data = response.json()
        self.assertEqual(len(data), len(expected))
        data.sort(key=lambda d: d['date'])
        for json, exp in zip(data, expected):
            self.assertDictEqual(json, exp)

    def test_payment(self):
        # prepare data
        self.client.login(username='Steven', password='Jobs')
        year = date.today().year
        ev_data = {
            'title': 'Title4',
            'city': 'City3',
            'cost': 500,
            'tickets': 1,
            'date': date(year, 7, 3),
            'periodicity': 'one-off',
            'id': 10
        }
        ev = Event.objects.create(**ev_data)
        ev_data['date'] = datetimestr(ev_data['date'])
        data = {
            'user_id': 1,
            'event': 10,
            'transaction_id': 1,
            'date': datetimestr(ev.date),
        }
        # check payment
        response = self.client.post('/buy-ticket', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # check tickets number changed
        expected = ev_data
        expected['tickets'] -= 1
        response = self.client.get('/event/10')
        self.assertEqual(response.json(), ev_data)
        # get no-tickets response
        response = self.client.post('/buy-ticket', data=data)
        expected['tickets'] -= 1
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)


def datetimestr(dt):
    return datetime.strftime(dt, '%Y-%m-%d')
