# Generated by Django 4.0.8 on 2022-10-28 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_calendar', '0010_alter_addressbook_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addressbook',
            name='owner',
        ),
        migrations.AddField(
            model_name='address',
            name='address_book',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule_calendar.addressbook'),
        ),
    ]
