from django import forms
from .models import Empleado, ConfiguracionGeneral, Grado
from django.forms import CheckboxInput, DateInput


class ConfiguracionGeneralForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionGeneral
        fields = ['nombre_institucion', 'nombre_institucion2', 'direccion', 'logotipo', 'tel', 'sitio_web', 'correo']
        
    # Personalizamos la clase 'form-control' para otros campos si es necesario
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Añadimos 'form-control' a los campos, si no está especificado en los widgets
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombres', 'apellidos', 'grado', 'imagen', 'tel']

    # Personalizar los campos para agregar la clase 'form-control'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar la clase 'form-control' a todos los campos del formulario
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
        
        # Si hay algún campo relacionado, como "grado", se personaliza aquí
        self.fields['grado'].queryset = Grado.objects.all()  # Se asegura de que solo se muestren los grados disponibles.



class EmpleadoEditForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombres', 'apellidos', 'grado', 'imagen', 'tel', 'activo']
        labels = {'activo': 'Activo'}
        widgets = {
            'grado': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tel': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizar los campos para agregar la clase 'form-control' en todos los campos si no está especificado
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

        # Personalizar el queryset del campo 'grado' para asegurar que solo se muestren los grados disponibles
        self.fields['grado'].queryset = Grado.objects.all()
