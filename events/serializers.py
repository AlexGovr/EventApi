
from rest_framework import serializers


class EventQuerySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=60)
    tickets = serializers.IntegerField()
    cost = serializers.FloatField()
    date = serializers.DateTimeField()
