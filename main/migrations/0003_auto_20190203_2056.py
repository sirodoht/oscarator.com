# Generated by Django 2.1.5 on 2019-02-03 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0002_category_entry_vote")]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="year",
            field=models.PositiveSmallIntegerField(default=2019),
        )
    ]