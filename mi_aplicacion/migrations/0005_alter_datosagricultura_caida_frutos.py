# Generated by Django 5.1.1 on 2024-10-04 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mi_aplicacion', '0004_rename_radiacion_solar_datosagricultura_radiacion_solar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datosagricultura',
            name='Caida_Frutos',
            field=models.IntegerField(),
        ),
    ]
