from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('create/', views.course_create, name='course_create'),
    path('<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('<int:course_id>/enroll/', views.course_enroll, name='course_enroll'),
    path('<int:course_id>/unenroll/', views.course_unenroll, name='course_unenroll'),
    path('my-courses/', views.my_courses, name='my_courses'),
]
