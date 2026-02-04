from django.urls import path
from . import views

app_name = "bible"

urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("<slug:book_slug>/", views.chapter_list, name="chapter_list"),
    path("<slug:book_slug>/<int:chapter_number>/", views.chapter_view, name="chapter_view"),
]
