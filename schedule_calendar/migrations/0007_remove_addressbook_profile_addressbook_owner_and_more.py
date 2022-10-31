# Generated by Django 4.0.8 on 2022-10-25 13:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule_calendar', '0006_remove_profile_address_book_addressbook_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addressbook',
            name='profile',
        ),
        migrations.AddField(
            model_name='addressbook',
            name='owner',
            field=models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='schedule_calendar.profile'),
        ),
        migrations.AlterField(
            model_name='addressbook',
            name='contacts',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL),
        ),
    ]
