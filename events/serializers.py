
from rest_framework import serializers
from .models import Transaction


class EventQuerySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=60)
    tickets = serializers.IntegerField()
    cost = serializers.FloatField()
    date = serializers.DateTimeField()


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only = '__all__'
