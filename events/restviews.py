
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Event
from .serializers import EventQuerySerializer


class EventQueryViewset(viewsets.ViewSet):

    months = ('dec', 'jan', 'feb',
              'mar', 'apr', 'may',
              'jun', 'jul', 'aug',
              'sep', 'oct', 'nov')

    @action(detail=False, url_path='upcoming')
    def get_upcoming_occurrences(self, request):
        city = request.get('city')
        if city is None:
            return r404({'detail': f'city value must be specified'})
        objects = Event.get_upcoming_occurences(city)
        srl = EventQuerySerializer(objects, many=True)
        return Response(srl.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='month')
    def get_month_occurrences(self, request):
        month = request.query_params.get('month')
        if month is None:
            return r404({'detail': f'month value must be specified'})
        try:
            month = datetime.strptime(month, '%b').month
        except:
            r404({'detail': f'month value must be one of {self.months}'})
        objects = Event.get_month_occurrences(month)
        srl = EventQuerySerializer(objects, many=True)
        return Response(srl.data, status=status.HTTP_200_OK)


def r404(data):
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
