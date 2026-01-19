from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("todos/", views.todos, name="todos"),
    path("account/", views.users, name="account"),
    path("database/", views.in_database, name="in_database"),
    path("sessions/", view=views.user_sessions, name="user_sessions"),
]