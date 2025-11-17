from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('course/<int:course_id>/create/', views.create_course_chat_room, name='create_course_chat'),
    path('dm/<int:user_id>/', views.create_direct_message, name='create_dm'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('room/<int:room_id>/load-more/', views.load_more_messages, name='load_more_messages'),
    path('notifications/count/', views.notifications_count, name='notifications_count'),
]
