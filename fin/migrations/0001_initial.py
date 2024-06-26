# Generated by Django 5.0.4 on 2024-04-14 09:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Données',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nom', models.CharField(max_length=100)),
                ('date', models.DateField(unique=True)),
                ('Valuer', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('city', models.CharField(max_length=100)),
                ('new_column', models.CharField(blank=True, max_length=100, null=True)),
                ('date', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='client',
            fields=[
                ('clientId', models.AutoField(primary_key=True, serialize=False)),
                ('clientName', models.CharField(max_length=500)),
                ('clientAdresse', models.CharField(default=' ', max_length=500)),
                ('clientActivity', models.CharField(default=' ', max_length=500)),
                ('id_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='dataimport',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(default=' ', max_length=100)),
                ('description', models.CharField(default=' ', max_length=700)),
                ('client', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='fin.client')),
            ],
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(max_length=50)),
                ('numero_facture', models.CharField(max_length=100)),
                ('nom_fournisseur', models.CharField(max_length=255)),
                ('libelle', models.CharField(max_length=255)),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantite', models.IntegerField()),
                ('tva', models.DecimalField(decimal_places=2, max_digits=5)),
                ('total_hors_taxe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_ttc', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('catéogorie', models.CharField(default=' ', max_length=70)),
                ('fichier', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='fin.dataimport')),
            ],
        ),
        migrations.CreateModel(
            name='UserClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fin.client')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'client')},
            },
        ),
    ]
