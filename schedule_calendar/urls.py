from django.urls import path, include
from . import views, email_handling

app_name = 'schedule_calendar'

urlpatterns = [
    path('', views.index),
    path('accounts/', include('django.contrib.auth.urls')),
    path('verifying/', views.verifying, name='verifying'),
    path('activate/<uidb64>/<token>', email_handling.activate, name='activate'),
    path('signup/', views.signup, name='signup'),
    path('profile/edit/', views.profile, name='profile'),
    path('logout/', views.index),

    path('check_if_user_exists/<check_user>', views.address_book, name='check_if_user'),
    path('address_book/<check_user>', views.address_book, name='address_book'),

    path('calendar/', views.CalendarView.as_view(), name='calendar'),

    path('event/new/', views.event, name='event_new'),
    path('calendar/event/edit/<event_id>/', views.event, name='event_edit'),
    path('event_delete/', views.event_delete, name='event_delete'),

    path('invite/', views.invite, name='invite'),
    path('invite_result/<uidb64>/<token>/<participant>/<result>', email_handling.invite_result, name='invite_result'),
    path('invite_response/', views.invite_response, name='invite_response'),
    path('remove_participant/', views.remove_participant, name='remove_participant'),
]
