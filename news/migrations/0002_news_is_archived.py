# Generated by Django 5.1.7 on 2025-05-07 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]
