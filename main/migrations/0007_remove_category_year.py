# Generated by Django 2.1.5 on 2020-01-25 21:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("main", "0006_entry_is_winner")]

    operations = [migrations.RemoveField(model_name="category", name="year")]