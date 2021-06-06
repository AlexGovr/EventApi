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
        default='one-off')

    @classmethod
    def get_month_occurrences(cls, month):
        return cls.objects.all()
    
    @classmethod
    def get_upcoming_occurences(cls, city):
        return cls.objects.filter(city=city)
