# Generated by Django 4.2 on 2023-04-23 14:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]