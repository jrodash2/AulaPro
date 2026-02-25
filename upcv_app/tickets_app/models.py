from django.db import models
from django.contrib.auth.models import User

class TipoEquipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Oficina(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('cerrado', 'Cerrado'),
        ('pendiente', 'Pendiente'),
    ]
    
    VIA_CONTACTO_CHOICES = [
        ('telefono', 'Telefono'),
        ('wahtsapp', 'WhatsApp'),
        ('personal ', 'Personal'),
        ('correo', 'Correo'),
    ]

    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True)
    via_contacto = models.CharField(max_length=100, choices=VIA_CONTACTO_CHOICES, default='telefono')
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.SET_NULL, null=True)
    problema = models.CharField(max_length=200)
    responsable = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(max_length=100, blank=True)
    detalle_problema = models.TextField(blank=True)
    solucion_problema = models.TextField(blank=True)
    tecnico_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tickets_asignados')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='alta')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.problema} ({self.estado})"