from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('week/', views.week_view, name='week'),
    path('day/', views.day_view, name='day'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
]
