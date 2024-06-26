# Generated by Django 3.2.12 on 2024-05-07 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fin', '0011_auto_20240507_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dim_Produit',
            fields=[
                ('id_produit', models.AutoField(primary_key=True, serialize=False)),
                ('libelle', models.CharField(max_length=100)),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Dim_Temps',
            fields=[
                ('id_temps', models.AutoField(primary_key=True, serialize=False)),
                ('id_Tempss', models.CharField(max_length=500)),
                ('jour', models.CharField(max_length=2)),
                ('mois', models.CharField(max_length=2)),
                ('annee', models.IntegerField()),
            ],
        ),
    ]
