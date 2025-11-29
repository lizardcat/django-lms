from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # Student AI Assistance
    path('quiz/<int:assignment_id>/', views.quiz_assistant, name='quiz_assistant'),
    path('quiz/<int:assignment_id>/hint/', views.get_hint, name='get_hint'),
    path('quiz/<int:assignment_id>/explain/', views.explain_concept, name='explain_concept'),
    path('quiz/<int:assignment_id>/review/', views.review_answer, name='review_answer'),
    path('study/<int:submission_id>/', views.study_recommendations, name='study_recommendations'),

    # Teacher AI Assistance
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('grading/<int:course_id>/', views.grading_assistant, name='grading_assistant'),
    path('grading/suggest/<int:submission_id>/', views.generate_grading_suggestion, name='generate_grading_suggestion'),
    path('grading/accept/<int:submission_id>/', views.accept_grading_suggestion, name='accept_grading_suggestion'),

    # Student Analytics
    path('analytics/<int:course_id>/', views.student_analytics_view, name='student_analytics'),
    path('analytics/<int:course_id>/student/<int:student_id>/', views.student_detail_analytics, name='student_detail_analytics'),
    path('analytics/<int:course_id>/student/<int:student_id>/refresh/', views.refresh_analytics, name='refresh_analytics'),
]
