# Generated by Django 3.2.12 on 2024-04-29 06:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fin', '0004_alter_client_clientname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facture',
            name='date',
        ),
        migrations.AddField(
            model_name='facture',
            name='Date',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 1, 0, 0), max_length=50),
        ),
    ]
