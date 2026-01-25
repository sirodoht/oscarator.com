from django.contrib import admin
from django.urls import path

from main import views

admin.site.site_header = "Oscarator administration"
app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("enter/", views.enter, name="enter"),
    path("join/", views.join, name="join"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("reset-password/", views.forgot, name="forgot"),
    path(
        "reset-password/<uidb64>/<token>/", views.forgot_confirm, name="forgot_confirm"
    ),
    path("@<username>/", views.user, name="user"),
    path("@<username>/<int:year>/", views.user_year, name="user_year"),
    path("settings/", views.preferences, name="preferences"),
    path("edition/<int:year>/", views.edition, name="edition"),
    path("hall-of-fame/", views.hall_of_fame, name="hall_of_fame"),
    path("hall-of-fame/<int:year>/", views.hall_of_fame_year, name="hall_of_fame_year"),
]
