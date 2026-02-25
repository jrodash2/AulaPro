from django import forms

from .models import Alumno, Carrera, ConfiguracionGeneral, Establecimiento, Grado, Matricula


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-control"
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            field.widget.attrs["class"] = f"{field.widget.attrs.get('class', '')} {css_class}".strip()


class ConfiguracionGeneralForm(BootstrapModelForm):
    class Meta:
        model = ConfiguracionGeneral
        fields = ["nombre_institucion", "nombre_institucion2", "direccion", "logotipo", "tel", "sitio_web", "correo"]


class AlumnoForm(BootstrapModelForm):
    class Meta:
        model = Alumno
        fields = ["codigo_personal", "nombres", "apellidos", "fecha_nacimiento", "cui", "grado", "imagen", "tel", "activo"]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }


class EstablecimientoForm(BootstrapModelForm):
    class Meta:
        model = Establecimiento
        fields = ["nombre", "direccion", "fondo_gafete", "gafete_ancho", "gafete_alto", "activo"]


class CarreraForm(BootstrapModelForm):
    class Meta:
        model = Carrera
        fields = ["establecimiento", "nombre", "activo"]


class GradoForm(BootstrapModelForm):
    class Meta:
        model = Grado
        fields = ["carrera", "nombre", "descripcion", "jornada", "seccion", "activo"]


class MatriculaForm(BootstrapModelForm):
    class Meta:
        model = Matricula
        fields = ["alumno", "grado", "ciclo", "activo"]

    def __init__(self, *args, **kwargs):
        establecimiento_id = kwargs.pop("establecimiento_id", None)
        carrera_id = kwargs.pop("carrera_id", None)
        super().__init__(*args, **kwargs)
        self.fields["alumno"].queryset = Alumno.objects.order_by("apellidos", "nombres")
        grados = Grado.objects.select_related("carrera", "carrera__establecimiento")
        if establecimiento_id:
            grados = grados.filter(carrera__establecimiento_id=establecimiento_id)
        if carrera_id:
            grados = grados.filter(carrera_id=carrera_id)
        self.fields["grado"].queryset = grados
