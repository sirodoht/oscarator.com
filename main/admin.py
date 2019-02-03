from django.contrib import admin

from main import models

admin.site.register(models.Profile)
admin.site.register(models.Analytic)
admin.site.register(models.Category)
admin.site.register(models.Entry)
admin.site.register(models.Vote)
