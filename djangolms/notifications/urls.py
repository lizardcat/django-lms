from django.urls import path
from . import views

urlpatterns = [
    # Announcement URLs
    path('course/<int:course_id>/announcements/', views.course_announcements, name='course_announcements'),
    path('announcement/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
    path('course/<int:course_id>/announcement/new/', views.create_announcement, name='create_announcement'),
    path('announcement/<int:announcement_id>/edit/', views.edit_announcement, name='edit_announcement'),
    path('announcement/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),

    # Notification URLs
    path('notifications/', views.notification_list, name='notification_list'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notification/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/clear/', views.clear_all_notifications, name='clear_all_notifications'),
]
