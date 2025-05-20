from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer, EventListSerializer

class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all().order_by('-event_date')
    serializer_class = EventListSerializer

class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"}, 
                status=status.HTTP_404_NOT_FOUND
            ) 