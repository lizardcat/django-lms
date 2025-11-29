from django.urls import path
from . import views

app_name = 'livestream'

urlpatterns = [
    path('', views.livestream_list, name='livestream_list'),
    path('stream/<int:stream_id>/', views.stream_view, name='stream_view'),
    path('stream/<int:stream_id>/detail/', views.stream_detail, name='stream_detail'),
    path('course/<int:course_id>/create/', views.create_stream, name='create_stream'),
    path('stream/<int:stream_id>/start/', views.start_stream, name='start_stream'),
    path('stream/<int:stream_id>/end/', views.end_stream, name='end_stream'),
    path('question/<int:question_id>/answer/', views.answer_question, name='answer_question'),
    path('question/<int:question_id>/pin/', views.pin_question, name='pin_question'),
    path('recording/<int:recording_id>/', views.recording_view, name='recording_view'),
]
