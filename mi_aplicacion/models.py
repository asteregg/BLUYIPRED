from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import uuid

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    token = models.UUIDField(null=True, blank=True)  # Campo para el token
    token_expires = models.DateTimeField(null=True, blank=True)  # Campo para la expiración del token


    def is_token_valid(self):
        return self.token_expires > timezone.now() if self.token_expires else False  # Método para validar si el token es válido

    def __str__(self):
        return self.name
# Create your models here.
class DatosAgricultura(models.Model):
    pkuser=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    Temp_Max = models.FloatField()
    Temp_Min = models.FloatField()
    Humedad = models.FloatField()
    Radiacion_Solar = models.FloatField()
    Viento = models.FloatField()
    Precipitacion = models.FloatField()
    pH_Suelo = models.FloatField()
    Nitrogeno = models.FloatField()
    Fertilizacion = models.FloatField()
    Densidad = models.FloatField()
    N_Flores = models.IntegerField()
    Plagas = models.IntegerField()
    Caida_Frutos = models.FloatField()
    Rendimiento = models.FloatField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

class reportes (models.Model):
    pkdatos=models.ForeignKey(DatosAgricultura, on_delete=models.CASCADE)
    pkuser=models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

class Recomendacion(models.Model):
    reporte = models.ForeignKey(reportes, on_delete=models.CASCADE, related_name='recomendaciones')
    rclimaticas = models.TextField()
    rsuelo = models.TextField()
    ragronomicas = models.TextField()
    rfenologicos = models.TextField()
    rplagas = models.TextField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)