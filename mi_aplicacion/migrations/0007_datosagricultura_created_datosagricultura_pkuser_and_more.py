# Generated by Django 5.1.1 on 2024-10-26 02:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mi_aplicacion', '0006_user_alter_datosagricultura_caida_frutos'),
    ]

    operations = [
        migrations.AddField(
            model_name='datosagricultura',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='datosagricultura',
            name='pkuser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mi_aplicacion.user'),
        ),
        migrations.AddField(
            model_name='datosagricultura',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='token_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128),
        ),
        migrations.CreateModel(
            name='reportes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('pkdatos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mi_aplicacion.datosagricultura')),
                ('pkuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mi_aplicacion.user')),
            ],
        ),
        migrations.CreateModel(
            name='Recomendacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rclimaticas', models.TextField()),
                ('rsuelo', models.TextField()),
                ('ragronomicas', models.TextField()),
                ('rfenologicos', models.TextField()),
                ('rplagas', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recomendaciones', to='mi_aplicacion.reportes')),
            ],
        ),
    ]
