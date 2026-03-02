from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("ping/", views.ping, name="ping"),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("settings/", views.settings_page, name="settings"),
    path("lesson-1/", views.lesson_1_hub, name="lesson_1_hub"),
    path("lesson-1/alphabet-learn/", views.alphabet_learn, name="alphabet_learn"),
    path("lesson-2/", views.lesson_2_hub, name="lesson_2_hub"),
    path("lesson-2/similar-letters/", views.similar_letters, name="similar_letters"),
    path("lesson-2/begadkefat/", views.begadkefat, name="begadkefat"),
    path("lesson-2/final-letters/", views.final_letters, name="final_letters"),
    path("lesson/<slug:lesson_slug>/", views.lesson_runner, name="lesson_runner"),
    path("lesson/<slug:lesson_slug>/review/", views.review_lesson, name="review_lesson"),
]