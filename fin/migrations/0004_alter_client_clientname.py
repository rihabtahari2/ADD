# Generated by Django 3.2.12 on 2024-04-23 08:37

from django.db import migrations, models
import fin.models


class Migration(migrations.Migration):

    dependencies = [
        ('fin', '0003_client_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='clientName',
            field=models.CharField(max_length=500, validators=[fin.models.validate_caracteres]),
        ),
    ]
