from django.contrib import admin
from django.urls import path

from main import views

admin.site.site_header = "Oscarator administration"
app_name = "main"

urlpatterns = [path("", views.index, name="index")]
