from datetime import date

from django import forms

from empleados_app.forms import BaseRihoForm
from empleados_app.models import Matricula


class MatriculaFiltroForm(forms.Form):
    ciclo = forms.IntegerField(required=False)
    estado = forms.ChoiceField(
        required=False,
        choices=(('', 'Todos'), ('activo', 'Activo'), ('inactivo', 'Inactivo')),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MatricularPorCodigoForm(BaseRihoForm):
    codigo_personal = forms.CharField(max_length=30)

    class Meta:
        model = Matricula
        fields = ['ciclo', 'estado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo_personal'].widget.attrs['class'] = 'form-control'
        self.fields['codigo_personal'].widget.attrs['placeholder'] = 'Ej. A-1001'
        self.fields['ciclo'].initial = date.today().year
