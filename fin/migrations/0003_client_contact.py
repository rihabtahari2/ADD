# Generated by Django 3.2.12 on 2024-04-22 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fin', '0002_facture_nom_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='contact',
            field=models.EmailField(default='example@example.com', max_length=254),
        ),
    ]
