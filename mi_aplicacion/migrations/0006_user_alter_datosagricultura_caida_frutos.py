# Generated by Django 5.1.1 on 2024-10-05 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mi_aplicacion', '0005_alter_datosagricultura_caida_frutos'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='datosagricultura',
            name='Caida_Frutos',
            field=models.FloatField(),
        ),
    ]
