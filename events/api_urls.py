from django.urls import path
from .api_views import EventDetailAPIView, EventListAPIView

app_name = 'events_api'

urlpatterns = [
    path('events/', EventListAPIView.as_view(), name='event_list'),
    path('events/<int:id>/', EventDetailAPIView.as_view(), name='event_detail'),
] 