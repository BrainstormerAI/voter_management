# Generated by Django 5.1.7 on 2025-05-12 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0003_rename_is_archived_news_archived_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="news",
            old_name="feature_image",
            new_name="featured_image",
        ),
    ]
