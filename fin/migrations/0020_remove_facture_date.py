# Generated by Django 3.2.12 on 2024-05-25 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fin', '0019_auto_20240520_1243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facture',
            name='Date',
        ),
    ]
