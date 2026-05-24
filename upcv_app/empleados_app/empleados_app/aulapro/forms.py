from django import forms

from ..forms import BaseRihoForm
from ..models import CicloEscolar, ConfiguracionActualizacionAlumno, Empleado, Matricula


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


class ActualizacionPublicaAlumnoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ["fecha_nacimiento", "cui", "tel"]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"),
            "cui": forms.TextInput(attrs={"class": "form-control"}),
            "tel": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_nacimiento"].input_formats = ["%Y-%m-%d", "%d/%m/%Y"]
        if self.instance and self.instance.pk and self.instance.fecha_nacimiento:
            self.initial["fecha_nacimiento"] = self.instance.fecha_nacimiento.strftime("%Y-%m-%d")


class ConfiguracionActualizacionAlumnoForm(BaseRihoForm):
    fecha_inicio = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format="%Y-%m-%dT%H:%M"),
    )
    fecha_fin = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = ConfiguracionActualizacionAlumno
        fields = ["habilitado", "fecha_inicio", "fecha_fin"]
