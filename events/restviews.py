
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin
from .models import Event, Payment
from .serializers import (EventQuerySerializer,
                          EventSerializer,
                          PaymentSerializer)


class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]


class EventQueryViewset(viewsets.ViewSet):

    months = ('dec', 'jan', 'feb',
              'mar', 'apr', 'may',
              'jun', 'jul', 'aug',
              'sep', 'oct', 'nov')

    @action(detail=False, url_path='upcoming')
    def get_upcoming_occurrences(self, request):
        city = request.query_params.get('city')
        if city is None:
            return r400({'detail': f'city value must be specified'})
        objects = Event.get_upcoming_occurences(city)
        srl = EventQuerySerializer(objects, many=True)
        return Response(srl.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='month')
    def get_month_occurrences(self, request):
        month = request.query_params.get('month')
        title = request.query_params.get('title')
        if month is None:
            return r400({'detail': f'month value must be specified'})
        try:
            month = parse_month(month)
        except:
            return r400({'detail': f'month value must be one of {self.months}, not "{month}"'})
        objects = Event.get_month_occurrences(month, title)
        srl = EventQuerySerializer(objects, many=True)
        return Response(srl.data, status=status.HTTP_200_OK)


class PaymentViewSet(CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.none()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date = request.data.get('date')
        if date is None:
            return r400({'detail': 'date value must be specified'})
        try:
            date = parse_datestr(date)
        except:
            return r400({'detail': 'wrong date format'})
        payment = Payment(**serializer.validated_data)
        payment.save(date)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def r400(data):
    return Response(data, status=status.HTTP_400_BAD_REQUEST)


def parse_month(monthstr):
    return datetime.strptime(monthstr, '%b').month


def parse_datestr(s):
    return datetime.strptime(s, '%Y-%m-%d').date()
