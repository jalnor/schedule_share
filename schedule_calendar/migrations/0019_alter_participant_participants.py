# Generated by Django 4.0.8 on 2022-10-31 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_calendar', '0018_rename_participant_participant_participants_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='participants',
            field=models.ManyToManyField(blank=True, to='schedule_calendar.profile'),
        ),
    ]