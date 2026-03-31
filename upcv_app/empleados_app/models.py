from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from .gafete_utils import default_layout_front_back, normalizar_layout_gafete

DEFAULT_GAFETE_LAYOUT = default_layout_front_back("H")


class Establecimiento(models.Model):
    nombre = models.CharField(max_length=160, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    sitio_web = models.URLField(max_length=255, blank=True, null=True)
    background_gafete = models.ImageField(upload_to="logotipos2/", null=True, blank=True)
    background_gafete_posterior = models.ImageField(upload_to="logotipos2/", null=True, blank=True)
    gafete_ancho = models.PositiveIntegerField(default=880, validators=[MinValueValidator(500), MaxValueValidator(1800)])
    gafete_alto = models.PositiveIntegerField(default=565, validators=[MinValueValidator(300), MaxValueValidator(1200)])
    gafete_layout_json = models.JSONField(default=dict, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def get_layout(self):
        orientation = "V" if (self.gafete_alto or 0) > (self.gafete_ancho or 0) else "H"
        return normalizar_layout_gafete(self.gafete_layout_json or {}, orientation=orientation)

    def get_ciclo_activo(self):
        return self.ciclos_escolares.filter(activo=True).order_by("-anio", "-id").first()


class CicloEscolar(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="ciclos_escolares")
    nombre = models.CharField(max_length=50)
    anio = models.PositiveIntegerField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=False)

    class Meta:
        ordering = ["-anio", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["establecimiento", "nombre"], name="uq_ciclo_nombre_establecimiento"),
            models.UniqueConstraint(
                fields=["establecimiento"],
                condition=Q(activo=True),
                name="uq_ciclo_activo_por_establecimiento",
            ),
        ]
        indexes = [
            models.Index(fields=["establecimiento", "activo"]),
            models.Index(fields=["establecimiento", "anio"]),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.establecimiento.nombre}"


class Carrera(models.Model):
    ciclo_escolar = models.ForeignKey(CicloEscolar, on_delete=models.CASCADE, related_name="carreras")
    nombre = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["ciclo_escolar__establecimiento__nombre", "ciclo_escolar__anio", "nombre"]
        unique_together = ("ciclo_escolar", "nombre")

    def __str__(self):
        return f"{self.nombre} - {self.ciclo_escolar.nombre}"


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
    tel = models.CharField(max_length=15, null=True, blank=True)
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
            grado_establecimiento_id = self.grado.carrera.ciclo_escolar.establecimiento_id
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


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    foto = models.ImageField(upload_to="perfil_usuario/", null=True, blank=True)
    establecimiento_gestionado = models.ForeignKey(
        Establecimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gestores_asignados",
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Curso(models.Model):
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="cursos")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} - {self.grado.nombre}"


class CursoDocente(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="docentes_asignados")
    docente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cursos_asignados")
    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["curso", "docente"], name="uq_curso_docente"),
        ]

    def clean(self):
        super().clean()
        if self.docente_id and not self.docente.groups.filter(name="Docente").exists():
            raise ValidationError("El usuario asignado debe pertenecer al grupo Docente.")

    def __str__(self):
        return f"{self.curso.nombre} / {self.docente.username}"


class PeriodoAcademico(models.Model):
    TIPO_BIMESTRE = "BIMESTRE"
    TIPO_TRIMESTRE = "TRIMESTRE"
    TIPO_SEMESTRE = "SEMESTRE"
    TIPO_CHOICES = (
        (TIPO_BIMESTRE, "Bimestre"),
        (TIPO_TRIMESTRE, "Trimestre"),
        (TIPO_SEMESTRE, "Semestre"),
    )

    curso_docente = models.ForeignKey(CursoDocente, on_delete=models.CASCADE, related_name="periodos")
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES, default=TIPO_BIMESTRE)
    numero = models.PositiveSmallIntegerField()
    nombre = models.CharField(max_length=80)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tipo", "numero"]
        constraints = [
            models.UniqueConstraint(fields=["curso_docente", "tipo", "numero"], name="uq_periodo_curso_docente_tipo_numero"),
        ]

    def __str__(self):
        return self.nombre


class Asistencia(models.Model):
    curso_docente = models.ForeignKey(CursoDocente, on_delete=models.CASCADE, related_name="asistencias")
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE, related_name="asistencias", null=True, blank=True)
    fecha = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["curso_docente", "fecha"], name="uq_asistencia_curso_docente_fecha"),
            models.UniqueConstraint(fields=["periodo", "fecha"], name="uq_asistencia_periodo_fecha"),
        ]
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"{self.curso_docente} - {self.fecha}"


class AsistenciaDetalle(models.Model):
    asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE, related_name="detalles")
    alumno = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="asistencias_detalle")
    presente = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["asistencia", "alumno"], name="uq_asistencia_alumno"),
        ]

    def __str__(self):
        return f"{self.alumno} - {'Presente' if self.presente else 'Ausente'}"


class ObservacionAlumno(models.Model):
    TIPO_ACADEMICO = "academico"
    TIPO_CONDUCTA = "conducta"
    TIPO_ASISTENCIA = "asistencia"
    TIPO_OTRO = "otro"
    TIPO_CHOICES = (
        (TIPO_ACADEMICO, "Académico"),
        (TIPO_CONDUCTA, "Conducta"),
        (TIPO_ASISTENCIA, "Asistencia"),
        (TIPO_OTRO, "Otro"),
    )

    PRIORIDAD_BAJA = "baja"
    PRIORIDAD_MEDIA = "media"
    PRIORIDAD_ALTA = "alta"
    PRIORIDAD_CHOICES = (
        (PRIORIDAD_BAJA, "Baja"),
        (PRIORIDAD_MEDIA, "Media"),
        (PRIORIDAD_ALTA, "Alta"),
    )

    ESTADO_ABIERTA = "abierta"
    ESTADO_SEGUIMIENTO = "seguimiento"
    ESTADO_CERRADA = "cerrada"
    ESTADO_CHOICES = (
        (ESTADO_ABIERTA, "Abierta"),
        (ESTADO_SEGUIMIENTO, "En seguimiento"),
        (ESTADO_CERRADA, "Cerrada"),
    )

    alumno = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="observaciones")
    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_ACADEMICO)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default=PRIORIDAD_MEDIA)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default=ESTADO_ABIERTA)
    observacion = models.TextField()
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name="observaciones_alumnos_creadas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["alumno", "fecha"]),
            models.Index(fields=["alumno", "estado"]),
        ]

    def __str__(self):
        return f"{self.alumno} · {self.get_tipo_display()} · {self.fecha}"


# Alias de compatibilidad para evitar rupturas en imports antiguos
Alumno = Empleado
