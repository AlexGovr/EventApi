
from datetime import datetime, time, timedelta
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
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
        days_delta = -5
        print(datetimestr(days_delta))
        ev_data = {'title': 'Title4', 'city': 'City3', 'cost': 500,
             'tickets': 100, 'date': datetimestr(days_delta), 'periodicity': 'weekly'}
        e = Event(**ev_data)
        e.save()
        expected = [
            {**ev_data, 'date': datetimestr(days_delta + 7)},
            {**ev_data, 'date': datetimestr(days_delta + 14)},
            {**ev_data, 'date': datetimestr(days_delta + 21)},
            {**ev_data, 'date': datetimestr(days_delta + 28)},
        ]
        _ = [e.pop('periodicity') for e in expected]
        response = self.client.get('/get-events/upcoming?city=City3')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        msg=f'{response.json()}\n{expected}'
        print(*response.json(), sep='\n')
        print(*expected, sep='\n')
        self.assertEqual(response.json(), expected, msg=msg)

    def test_get_month(self):
        days_delta = -5
        print(datetimestr(days_delta))
        ev_data = {'title': 'Title5', 'city': 'City3', 'cost': 500,
             'tickets': 100, 'date': datetimestr(days_delta), 'periodicity': 'weekly'}
        e = Event(**ev_data)
        e.save()
        expected = [
            {**ev_data, 'date': datetimestr(days_delta + 7)},
            {**ev_data, 'date': datetimestr(days_delta + 14)},
            {**ev_data, 'date': datetimestr(days_delta + 21)},
            {**ev_data, 'date': datetimestr(days_delta + 28)},
        ]
        _ = [e.pop('periodicity') for e in expected]
        response = self.client.get('/get-events/month?month=june')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(response.data, {})

    # def test_payment(self):
    #     response = self.client.post('/buy-ticket', auth=('alex','1'), data={'user_id': 1, 'event': 1})
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
    #     self.assertEqual(response.data, {})


def datetimestr(days_delta=0):
    date = datetime.today() + timedelta(days=days_delta)
    return datetime.strftime(date, '%Y-%m-%dT%H:%M:%SZ')
