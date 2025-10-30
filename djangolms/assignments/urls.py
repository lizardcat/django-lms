from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/', views.assignment_list, name='assignment_list'),
    path('<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('course/<int:course_id>/create/', views.assignment_create, name='assignment_create'),
    path('<int:assignment_id>/edit/', views.assignment_edit, name='assignment_edit'),
    path('<int:assignment_id>/delete/', views.assignment_delete, name='assignment_delete'),
    path('<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]
