from django.contrib import admin

from .models import Carrera, CicloEscolar, ConfiguracionGeneral, Empleado, Establecimiento, Grado, Matricula


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("codigo_personal", "nombres", "apellidos", "establecimiento", "grado", "tel", "activo", "created_at")
    list_filter = ("activo", "establecimiento", "grado", "created_at")
    search_fields = ("codigo_personal", "nombres", "apellidos", "cui", "tel")


@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "activo", "gafete_ancho", "gafete_alto")
    list_filter = ("activo",)
    search_fields = ("nombre", "direccion")


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("nombre", "establecimiento", "activo")
    list_filter = ("establecimiento", "activo")
    search_fields = ("nombre", "establecimiento__nombre")


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "carrera", "jornada", "seccion", "activo")
    list_filter = ("carrera", "activo")
    search_fields = ("nombre", "descripcion")


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ("alumno", "grado", "ciclo_escolar", "estado", "created_at")
    list_filter = ("estado", "ciclo_escolar", "grado")
    search_fields = ("alumno__nombres", "alumno__apellidos")


@admin.register(ConfiguracionGeneral)
class ConfiguracionGeneralAdmin(admin.ModelAdmin):
    list_display = ("nombre_institucion", "direccion", "tel", "sitio_web", "correo")
    search_fields = ("nombre_institucion", "direccion", "correo")


@admin.register(CicloEscolar)
class CicloEscolarAdmin(admin.ModelAdmin):
    list_display = ("nombre", "establecimiento", "anio", "estado", "es_activo")
    list_filter = ("establecimiento", "estado", "es_activo")
    search_fields = ("nombre", "establecimiento__nombre")
