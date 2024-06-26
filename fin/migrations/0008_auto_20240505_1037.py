# Generated by Django 3.2.12 on 2024-05-05 08:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fin', '0007_facture_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpertProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AssistantProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='dataimport',
            name='Assistantprofile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fin.assistantprofile'),
        ),
        migrations.AddField(
            model_name='dataimport',
            name='Expertprofile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fin.expertprofile'),
        ),
    ]
