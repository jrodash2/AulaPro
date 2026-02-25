from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Grado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    grado = models.ForeignKey(Grado, on_delete=models.SET_NULL, null=True, blank=True)
    imagen = models.ImageField(upload_to='card_images/', null=True, blank=True)
    tel = models.CharField(max_length=15, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='empleados')


    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ConfiguracionGeneral(models.Model):
    nombre_institucion = models.CharField(max_length=255, verbose_name='Nombre de la Institución')
    nombre_institucion2 = models.CharField(max_length=255, verbose_name='Nombre de la Institución2')
    direccion = models.CharField(max_length=255, verbose_name='Dirección')
    logotipo = models.ImageField(upload_to='logotipos/', verbose_name='Logotipo', null=True, blank=True)
    tel = models.CharField(max_length=15, unique=True, null=False, blank=False)
    sitio_web = models.URLField(max_length=255, verbose_name='Sitio Web', null=True, blank=True)  # Nuevo campo para el sitio web
    correo = models.EmailField(max_length=255, verbose_name='Correo Electrónico', null=True, blank=True)  # Nuevo campo para el correo

    def __str__(self):
        return self.nombre_institucion