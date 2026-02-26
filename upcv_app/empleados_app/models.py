from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


DEFAULT_GAFETE_LAYOUT = {
    "canvas": {"width": 880, "height": 565},
    "fields": [
        {
            "key": "nombres",
            "label": "Nombres",
            "x": 300,
            "y": 120,
            "font_size": 45,
            "font_weight": "700",
            "color": "#090909",
            "align": "left",
            "class_css": "t5",
            "visible": True,
        },
        {
            "key": "apellidos",
            "label": "Apellidos",
            "x": 300,
            "y": 180,
            "font_size": 50,
            "font_weight": "400",
            "color": "#111111",
            "align": "left",
            "class_css": "t6",
            "visible": True,
        },
        {
            "key": "grado",
            "label": "Grado",
            "x": 350,
            "y": 260,
            "font_size": 25,
            "font_weight": "400",
            "color": "#090909",
            "align": "left",
            "class_css": "t7",
            "visible": True,
        },
        {
            "key": "grado_descripcion",
            "label": "Descripción grado",
            "x": 350,
            "y": 290,
            "font_size": 25,
            "font_weight": "400",
            "color": "#0f0f0f",
            "align": "left",
            "class_css": "t8",
            "visible": True,
        },
        {
            "key": "sitio_web",
            "label": "Sitio web",
            "x": 580,
            "y": 430,
            "font_size": 28,
            "font_weight": "400",
            "color": "#275393",
            "align": "left",
            "class_css": "t10",
            "visible": True,
        },
        {
            "key": "telefono_emergencia",
            "label": "Teléfono",
            "x": 520,
            "y": 500,
            "font_size": 35,
            "font_weight": "700",
            "color": "#030303",
            "align": "left",
            "class_css": "t11",
            "visible": True,
        },
    ],
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
        base = {"canvas": DEFAULT_GAFETE_LAYOUT["canvas"].copy(), "fields": [item.copy() for item in DEFAULT_GAFETE_LAYOUT["fields"]]}
        custom = self.gafete_layout_json or {}

        if isinstance(custom.get("canvas"), dict):
            base["canvas"]["width"] = int(custom["canvas"].get("width") or base["canvas"]["width"])
            base["canvas"]["height"] = int(custom["canvas"].get("height") or base["canvas"]["height"])

        if isinstance(custom.get("fields"), list):
            by_key = {f["key"]: f for f in base["fields"]}
            for field in custom["fields"]:
                if not isinstance(field, dict):
                    continue
                key = field.get("key")
                if key in by_key:
                    by_key[key].update(field)
            base["fields"] = [by_key[k] for k in by_key]
        elif isinstance(custom.get("layers"), dict):
            # Compatibilidad hacia atrás con layouts antiguos por clases
            by_key = {f["key"]: f for f in base["fields"]}
            alias = {"telefono": "telefono_emergencia"}
            for key, cfg in custom["layers"].items():
                if not isinstance(cfg, dict):
                    continue
                target = alias.get(key, key)
                if target in by_key and cfg.get("class"):
                    by_key[target]["class_css"] = cfg.get("class")
            base["fields"] = [by_key[k] for k in by_key]

        return base

    def get_ciclo_activo(self):
        return self.ciclos_escolares.filter(es_activo=True).order_by("-anio", "-id").first()


class CicloEscolar(models.Model):
    ESTADOS = (("activo", "Activo"), ("inactivo", "Inactivo"))

    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="ciclos_escolares")
    nombre = models.CharField(max_length=50)
    anio = models.PositiveIntegerField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    es_activo = models.BooleanField(default=False)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="activo")

    class Meta:
        ordering = ["-anio", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["establecimiento", "nombre"], name="uq_ciclo_nombre_establecimiento"),
            models.UniqueConstraint(
                fields=["establecimiento"],
                condition=Q(es_activo=True),
                name="uq_ciclo_activo_por_establecimiento",
            ),
        ]
        indexes = [
            models.Index(fields=["establecimiento", "es_activo"]),
            models.Index(fields=["establecimiento", "anio"]),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.establecimiento.nombre}"


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
    ciclo = models.PositiveIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2200)], null=True, blank=True)
    ciclo_escolar = models.ForeignKey(CicloEscolar, on_delete=models.PROTECT, null=True, blank=True, related_name="matriculas")
    estado = models.CharField(max_length=10, choices=ESTADOS, default="activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "alumno__apellidos", "alumno__nombres"]
        constraints = [
            models.UniqueConstraint(
                fields=["alumno", "grado", "ciclo_escolar"],
                condition=Q(ciclo_escolar__isnull=False),
                name="uq_matricula_alumno_grado_ciclo_escolar",
            )
        ]
        indexes = [
            models.Index(fields=["grado", "estado"]),
            models.Index(fields=["grado", "ciclo_escolar"]),
        ]

    def clean(self):
        super().clean()
        if not self.ciclo_escolar_id or not self.grado_id:
            return
        grado_establecimiento_id = None
        if self.grado and self.grado.carrera:
            grado_establecimiento_id = self.grado.carrera.establecimiento_id
        if grado_establecimiento_id and self.ciclo_escolar.establecimiento_id != grado_establecimiento_id:
            raise ValidationError("El ciclo escolar no pertenece al establecimiento del grado.")

    def __str__(self):
        ciclo_nombre = self.ciclo_escolar.nombre if self.ciclo_escolar_id else (self.ciclo or "-")
        return f"{self.alumno} / {self.grado} / {ciclo_nombre}"


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
