from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


DEFAULT_GAFETE_LAYOUT = {
    "background": "",
    "layers": {
        "nombres": {"class": "t5"},
        "apellidos": {"class": "t6"},
        "grado": {"class": "t7"},
        "grado_descripcion": {"class": "t8"},
        "sitio_web": {"class": "t10"},
        "telefono": {"class": "t11"},
    },
}


class Establecimiento(models.Model):
    nombre = models.CharField(max_length=160, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    background_gafete = models.ImageField(upload_to="logotipos2/", null=True, blank=True)
    gafete_ancho = models.PositiveIntegerField(default=880, validators=[MinValueValidator(500), MaxValueValidator(1800)])
    gafete_alto = models.PositiveIntegerField(default=565, validators=[MinValueValidator(300), MaxValueValidator(1200)])
    gafete_layout_json = models.JSONField(default=dict, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def get_layout(self):
        layout = DEFAULT_GAFETE_LAYOUT.copy()
        custom = self.gafete_layout_json or {}
        if custom.get("background"):
            layout["background"] = custom.get("background")
        if isinstance(custom.get("layers"), dict):
            merged_layers = layout["layers"].copy()
            for key, value in custom["layers"].items():
                if key in merged_layers and isinstance(value, dict):
                    merged_layers[key] = {**merged_layers[key], **value}
            layout["layers"] = merged_layers
        return layout


class Carrera(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="carreras")
    nombre = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["establecimiento__nombre", "nombre"]
        unique_together = ("establecimiento", "nombre")

    def __str__(self):
        return f"{self.nombre} - {self.establecimiento.nombre}"


class Grado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True, related_name="grados")
    jornada = models.CharField(max_length=30, blank=True)
    seccion = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    codigo_personal = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    cui = models.CharField(max_length=25, blank=True, null=True, db_index=True)
    grado = models.ForeignKey(Grado, on_delete=models.SET_NULL, null=True, blank=True)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name="alumnos")
    imagen = models.ImageField(upload_to="card_images/", null=True, blank=True)
    tel = models.CharField(max_length=15, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="empleados")

    class Meta:
        ordering = ["-created_at"]
        # Compatibilidad con bases ya migradas con RenameModel(Empleado -> Alumno)
        db_table = "empleados_app_alumno"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Matricula(models.Model):
    ESTADOS = (("activo", "Activo"), ("inactivo", "Inactivo"))

    alumno = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="matriculas")
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="matriculas")
    ciclo = models.PositiveIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2200)])
    estado = models.CharField(max_length=10, choices=ESTADOS, default="activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ciclo", "alumno__apellidos", "alumno__nombres"]
        unique_together = ("alumno", "grado", "ciclo")

    def __str__(self):
        return f"{self.alumno} / {self.grado} / {self.ciclo}"


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


# Alias de compatibilidad para evitar rupturas en imports antiguos
Alumno = Empleado
