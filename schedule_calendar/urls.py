from django.urls import path, include
from . import views

app_name = 'schedule_calendar'

urlpatterns = [
    path('', views.index),
    path('accounts/', include('django.contrib.auth.urls')),
    path('verifying/', views.verifying, name='verifying'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.index),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('calendar/event/edit/<event_id>/', views.event, name='event_edit'),
    path('invite/', views.invite, name='invite'),
    path('profile/edit/', views.profile, name='profile'),
    path('event_delete/', views.event_delete, name='event_delete'),
    path('remove_participant/', views.remove_participant, name='remove_participant'),
]
