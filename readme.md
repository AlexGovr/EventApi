
# Event API
## Set up
1. clone or download this repo
2. install all needed dependencies:
```pip install -r requirements.txt```
3. copy config files from config/example  to config/
4. create superuser
```python manage.py createsuperuser```
and change credentails in config/admin.py
5. migrate your database:
```python manage.py migrate```
6. run tests
```python manage.py test```
7. start Django server
```python manage.py runserver```
## API reference
An event is represented by a set of fields: id, title, city, date, periodicity, cost, tickets
periodicity value is one of: weekly, monthly, daily, yearly
# API methods
## Get a list of upcoming events for a specified city:
```GET /get-events/upcoming?city=<some-city>```
## Get a list of events for a specified month:
```GET /get-events/upcoming?month=<mon>```
Title value may be specified optionally
```/get-events/upcoming?month=<mon>&title=<some-title>```
For month use standard three-letter values (e.g. jan, may, dec, etc)
## Buy a ticket
```POST /buy-ticket```
A request must be authorized and provided with data containing user_id, transaction_id, event_id and event date
## Standart REST methods
Use ```/event/``` and ```/event/<id>``` authorized requests urls to manipulate events' data via GET, POST, PUT, PATCH and DELETE.
