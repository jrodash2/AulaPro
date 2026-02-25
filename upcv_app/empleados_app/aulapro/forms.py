from django import forms

from empleados_app.forms import BaseRihoForm
from empleados_app.models import CicloEscolar, Matricula


class MatriculaFiltroForm(forms.Form):
    ciclo_escolar = forms.ModelChoiceField(queryset=CicloEscolar.objects.none(), required=False, empty_label="Ciclo activo")
    estado = forms.ChoiceField(
        required=False,
        choices=(('', 'Todos'), ('activo', 'Activo'), ('inactivo', 'Inactivo')),
    )

    def __init__(self, *args, **kwargs):
        establecimiento = kwargs.pop('establecimiento', None)
        super().__init__(*args, **kwargs)
        if establecimiento:
            self.fields['ciclo_escolar'].queryset = CicloEscolar.objects.filter(establecimiento=establecimiento).order_by('-anio', '-id')
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MatricularPorCodigoForm(BaseRihoForm):
    codigo_personal = forms.CharField(max_length=30)

    class Meta:
        model = Matricula
        fields = ['estado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo_personal'].widget.attrs['class'] = 'form-control'
        self.fields['codigo_personal'].widget.attrs['placeholder'] = 'Ej. A-1001'
