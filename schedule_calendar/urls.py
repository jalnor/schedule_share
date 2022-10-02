from django.urls import path
from . import views

app_name = 'schedule_calendar'

urlpatterns = [
    path('', views.index),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('calendar/event/edit/<event_id>/', views.event, name='event_edit'),
]
