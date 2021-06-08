
from rest_framework import serializers
from .models import Event, Payment


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventQuerySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=60)
    tickets = serializers.IntegerField()
    cost = serializers.FloatField()
    date = serializers.DateTimeField()
    id = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        read_only = '__all__'
        exclude = ['cost']
