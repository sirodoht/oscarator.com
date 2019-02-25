from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Analytic(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=400, null=True, blank=True)
    querystring = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        return self.ip


class Category(models.Model):
    name = models.CharField(max_length=600)
    year = models.PositiveSmallIntegerField(default=timezone.now().year)

    def __str__(self):
        return self.name


class Entry(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=600)
    pic_url = models.CharField(max_length=1000)
    imdb = models.CharField(max_length=200, null=True, blank=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("user", "entry"),)

    def __str__(self):
        return self.entry.name + " - " + self.user.username
