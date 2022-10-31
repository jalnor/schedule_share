# Generated by Django 4.0.8 on 2022-10-24 00:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_calendar', '0005_addressbook_profile_address_book'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='address_book',
        ),
        migrations.AddField(
            model_name='addressbook',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule_calendar.profile'),
        ),
    ]
