from django.urls import path, include
from . import views

app_name = 'schedule_calendar'

urlpatterns = [
    path('', views.index),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('login/', views.index),
    path('logout/', views.index),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('calendar/event/edit/<event_id>/', views.event, name='event_edit'),
    path('add_participant/', views.add_participant, name='add_participant')
]
