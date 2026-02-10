from django.urls import path
from . import views
from .views import get_current_question, resume_lesson, start_lesson, submit_answer_view

app_name = "lessons"

urlpatterns = [
    path("start/", start_lesson, name="start_lesson"),
    path("<int:session_id>/current/", get_current_question, name="get_current_question"),
    path("<int:session_id>/submit/", submit_answer_view, name="submit_answer"),
    path("resume/", resume_lesson, name="resume_lesson"),
]