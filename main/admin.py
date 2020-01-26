from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from main import models


# User
class OscaratorAdmin(UserAdmin):
    list_display = ("username", "email", "date_joined", "last_login", "id")


admin.site.unregister(User)
admin.site.register(User, OscaratorAdmin)


# Profile
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "id")


admin.site.register(models.Profile, ProfileAdmin)


# Analytic
class AnalyticAdmin(admin.ModelAdmin):
    list_display = ("ip", "user", "created_at", "path", "querystring", "id")


admin.site.register(models.Analytic, AnalyticAdmin)


# Entry
class EntryAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "category", "is_winner", "imdb", "id")


admin.site.register(models.Entry, EntryAdmin)


# Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "id")


admin.site.register(models.Category, CategoryAdmin)


# Vote
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "entry", "created_at")


admin.site.register(models.Vote, VoteAdmin)
