from django.contrib import admin
from .models import Empleado, ConfiguracionGeneral, Grado

class EmpleadoAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista del admin
    list_display = ('nombres', 'apellidos', 'grado', 'tel', 'activo', 'created_at', 'updated_at', 'user')
    
    # Filtros disponibles para la vista de lista
    list_filter = ('activo', 'grado', 'created_at')
    
    # Campos por los que se puede buscar
    search_fields = ('nombres', 'apellidos', 'tel', 'user__username')
    
    # Jerarquía de fechas para facilitar la navegación por fecha
    date_hierarchy = 'created_at'
    
    # Campos a mostrar en el formulario de edición del admin
    fields = ('nombres', 'apellidos', 'grado', 'imagen', 'tel', 'user', 'activo')

    # Configuración para mostrar los campos en el formulario de manera adecuada
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Podemos agregar lógica adicional para modificar el formulario si es necesario
        return form


class ConfiguracionGeneralAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista del admin
    list_display = ('nombre_institucion', 'direccion', 'tel', 'sitio_web', 'correo', 'logotipo')
    
    # Campos por los que se puede buscar
    search_fields = ('nombre_institucion', 'direccion', 'sitio_web', 'correo')
    
    # Filtros disponibles para la vista de lista
    list_filter = ('nombre_institucion',)
    
    # Campos solo de lectura
    readonly_fields = ('id',)  # Solo lectura para el campo ID (si es un campo automático)
    
    # Definimos los campos que aparecerán en el formulario de edición
    fields = ('nombre_institucion', 'direccion', 'logotipo', 'tel', 'sitio_web', 'correo')

    # Configuración para mostrar los campos en el formulario de manera adecuada
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Podemos agregar lógica adicional para modificar el formulario si es necesario
        return form


# Registro del modelo, solo una vez
admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(ConfiguracionGeneral, ConfiguracionGeneralAdmin)
admin.site.register(Grado)  # Registramos el modelo Grado también, ya que lo estamos utilizando en el formulario de Empleado
