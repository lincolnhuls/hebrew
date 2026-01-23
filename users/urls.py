from django.urls import path
from . import views

urlpatterns = [
    path("account/", views.users, name="account"),
    path("sessions/", view=views.user_sessions, name="user_sessions"),
    path("logout/", view=views.user_logout, name="user_logout"),
]