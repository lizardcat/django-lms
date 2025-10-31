from django.urls import path
from . import views

urlpatterns = [
    # Gradebook views
    path('course/<int:course_id>/gradebook/', views.course_gradebook, name='course_gradebook'),
    path('course/<int:course_id>/my-grades/', views.student_grades, name='student_grades'),

    # Configuration
    path('course/<int:course_id>/configure/', views.grade_configuration, name='grade_configuration'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),

    # Grade management
    path('enrollment/<int:enrollment_id>/override/', views.override_grade, name='override_grade'),
    path('grade/<int:grade_id>/remove-override/', views.remove_override, name='remove_override'),
    path('course/<int:course_id>/recalculate/', views.recalculate_all_grades, name='recalculate_all_grades'),

    # Export
    path('course/<int:course_id>/export/', views.export_grades, name='export_grades'),
]
