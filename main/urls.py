from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("ping/", views.ping, name="ping"),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("settings/", views.settings_page, name="settings"),
    path("achievements/", views.achievements_page, name="achievements"),
    path("profile/", views.profile_page, name="profile"),
    path("lesson-1/", views.lesson_1_hub, name="lesson_1_hub"),
    path("lesson-1/alphabet-learn/", views.alphabet_learn, name="alphabet_learn"),
    path("lesson-3/", views.lesson_3_hub, name="lesson_3_hub"),
    path("lesson-3/vowels-learn/", views.vowels_learn, name="vowels_learn"),
    path("lesson-4/", views.lesson_4_hub, name="lesson_4_hub"),
    path("lesson-4/aspect-learn/", views.aspect_learn, name="aspect_learn"),
    path("lesson-5/", views.lesson_5_hub, name="lesson_5_hub"),
    path("lesson-5/suffixes-learn/", views.suffixes_learn, name="suffixes_learn"),
    path("lesson-6/", views.lesson_6_hub, name="lesson_6_hub"),
    path("lesson-6/prepositions-learn/", views.prepositions_learn, name="prepositions_learn"),
    path("lesson-2/", views.lesson_2_hub, name="lesson_2_hub"),
    path("lesson-2/similar-letters/", views.similar_letters, name="similar_letters"),
    path("lesson-2/begadkefat/", views.begadkefat, name="begadkefat"),
    path("lesson-2/final-letters/", views.final_letters, name="final_letters"),
    path("lesson/<slug:lesson_slug>/", views.lesson_runner, name="lesson_runner"),
    path("lesson/<slug:lesson_slug>/review/", views.review_lesson, name="review_lesson"),
]