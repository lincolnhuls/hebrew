from django.urls import path
from .views.auth import user_sessions, user_logout
from .views.pages import home, users
from .views.preferences import learning_preferences

app_name = "users"

urlpatterns = [
    path("account/", users, name="account"),
    path("sessions/", user_sessions, name="user_sessions"),
    path("logout/", user_logout, name="user_logout"),
    path("preferences/", learning_preferences, name="learning_preferences"),
]