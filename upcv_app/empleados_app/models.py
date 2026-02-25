from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


DEFAULT_GAFETE_LAYERS = [
    {"key": "nombres", "x": 120, "y": 130, "font_size": 26, "font_family": "Arial", "font_weight": "700", "color": "#1f2937", "align": "left", "max_width": 360},
    {"key": "apellidos", "x": 120, "y": 170, "font_size": 26, "font_family": "Arial", "font_weight": "700", "color": "#1f2937", "align": "left", "max_width": 360},
    {"key": "codigo_personal", "x": 120, "y": 220, "font_size": 18, "font_family": "Helvetica", "font_weight": "600", "color": "#374151", "align": "left", "max_width": 300},
    {"key": "cui", "x": 120, "y": 255, "font_size": 16, "font_family": "Helvetica", "font_weight": "500", "color": "#374151", "align": "left", "max_width": 320},
]


class Establecimiento(models.Model):
    nombre = models.CharField(max_length=180, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    fondo_gafete = models.ImageField(upload_to="logotipos2/", null=True, blank=True)
    gafete_ancho = models.PositiveIntegerField(default=1012, validators=[MinValueValidator(300), MaxValueValidator(3000)])
    gafete_alto = models.PositiveIntegerField(default=638, validators=[MinValueValidator(180), MaxValueValidator(2200)])
    gafete_capas = models.JSONField(default=list)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Establecimiento"
        verbose_name_plural = "Establecimientos"

    def __str__(self):
        return self.nombre

    def capas_por_defecto(self):
        return self.gafete_capas if self.gafete_capas else DEFAULT_GAFETE_LAYERS


class Carrera(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="carreras")
    nombre = models.CharField(max_length=180)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["establecimiento__nombre", "nombre"]
        unique_together = ("establecimiento", "nombre")

    def __str__(self):
        return f"{self.nombre} ({self.establecimiento})"


class Grado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, null=True, blank=True, related_name="grados")
    jornada = models.CharField(max_length=50, blank=True)
    seccion = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Alumno(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    codigo_personal = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    cui = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    grado = models.ForeignKey(Grado, on_delete=models.SET_NULL, null=True, blank=True)
    imagen = models.ImageField(upload_to="card_images/", null=True, blank=True)
    tel = models.CharField(max_length=15, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alumnos")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Matricula(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name="matriculas")
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="matriculas")
    ciclo = models.PositiveIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2200)])
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ciclo", "alumno__apellidos"]
        unique_together = ("alumno", "grado", "ciclo")

    def __str__(self):
        return f"{self.alumno} - {self.grado} ({self.ciclo})"


class ConfiguracionGeneral(models.Model):
    nombre_institucion = models.CharField(max_length=255, verbose_name="Nombre de la Institución")
    nombre_institucion2 = models.CharField(max_length=255, verbose_name="Nombre de la Institución2")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    logotipo = models.ImageField(upload_to="logotipos/", verbose_name="Logotipo", null=True, blank=True)
    tel = models.CharField(max_length=15, unique=True, null=False, blank=False)
    sitio_web = models.URLField(max_length=255, verbose_name="Sitio Web", null=True, blank=True)
    correo = models.EmailField(max_length=255, verbose_name="Correo Electrónico", null=True, blank=True)

    def __str__(self):
        return self.nombre_institucion
