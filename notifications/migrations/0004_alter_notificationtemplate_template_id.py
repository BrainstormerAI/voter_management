# Generated by Django 5.2 on 2025-04-15 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_alter_notificationtemplate_template_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='template_id',
            field=models.CharField(help_text='Edumarc SMS Template ID', max_length=100),
        ),
    ]
