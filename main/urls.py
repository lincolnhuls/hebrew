from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("settings/", views.settings_page, name="settings"),
    path("lesson-1/", views.lesson_1_hub, name="lesson_1_hub"),
    path("lesson-1/alphabet-learn/", views.alphabet_learn, name="alphabet_learn"),
    path("lesson/<slug:lesson_slug>/", views.lesson_runner, name="lesson_runner"),
]