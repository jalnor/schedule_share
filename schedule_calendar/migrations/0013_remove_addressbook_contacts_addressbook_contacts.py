# Generated by Django 4.0.8 on 2022-10-28 20:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule_calendar', '0012_remove_address_address_book_profile_address_book'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addressbook',
            name='contacts',
        ),
        migrations.AddField(
            model_name='addressbook',
            name='contacts',
            field=models.ManyToManyField(blank=True, null=True, related_name='contacts', to=settings.AUTH_USER_MODEL),
        ),
    ]
