from django.contrib import admin

from .models import Alumno, Carrera, ConfiguracionGeneral, Establecimiento, Grado, Matricula


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ("codigo_personal", "apellidos", "nombres", "grado", "cui", "activo", "created_at")
    list_filter = ("activo", "grado", "created_at")
    search_fields = ("codigo_personal", "nombres", "apellidos", "cui", "tel")


@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "activo", "gafete_ancho", "gafete_alto")
    list_filter = ("activo",)
    search_fields = ("nombre", "direccion")


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("nombre", "establecimiento", "activo")
    list_filter = ("activo", "establecimiento")
    search_fields = ("nombre", "establecimiento__nombre")


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "carrera", "jornada", "seccion", "activo")
    list_filter = ("activo", "carrera")
    search_fields = ("nombre", "descripcion", "carrera__nombre")


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ("alumno", "grado", "ciclo", "activo", "creado_en")
    list_filter = ("activo", "ciclo", "grado")
    search_fields = ("alumno__nombres", "alumno__apellidos", "grado__nombre")


@admin.register(ConfiguracionGeneral)
class ConfiguracionGeneralAdmin(admin.ModelAdmin):
    list_display = ("nombre_institucion", "direccion", "tel", "sitio_web", "correo")
    search_fields = ("nombre_institucion", "direccion", "sitio_web", "correo")
