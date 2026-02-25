from django import forms

from .models import Carrera, CicloEscolar, ConfiguracionGeneral, Empleado, Establecimiento, Grado, Matricula


class BaseRihoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                current = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{current} form-control".strip()


class ConfiguracionGeneralForm(BaseRihoForm):
    class Meta:
        model = ConfiguracionGeneral
        fields = ["nombre_institucion", "nombre_institucion2", "direccion", "logotipo", "tel", "sitio_web", "correo"]


class EmpleadoForm(BaseRihoForm):
    class Meta:
        model = Empleado
        fields = [
            "codigo_personal",
            "nombres",
            "apellidos",
            "fecha_nacimiento",
            "cui",
            "establecimiento",
            "grado",
            "imagen",
            "tel",
            "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }


class EmpleadoEditForm(EmpleadoForm):
    pass


class EstablecimientoForm(BaseRihoForm):
    class Meta:
        model = Establecimiento
        fields = ["nombre", "direccion", "background_gafete", "gafete_ancho", "gafete_alto", "activo"]


class CarreraForm(BaseRihoForm):
    class Meta:
        model = Carrera
        fields = ["establecimiento", "nombre", "activo"]


class GradoForm(BaseRihoForm):
    class Meta:
        model = Grado
        fields = ["carrera", "nombre", "descripcion", "jornada", "seccion", "activo"]


class CicloEscolarForm(BaseRihoForm):
    class Meta:
        model = CicloEscolar
        fields = ["nombre", "anio", "fecha_inicio", "fecha_fin", "estado", "es_activo"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre:
            raise forms.ValidationError("El nombre del ciclo escolar es obligatorio.")
        return nombre


class MatriculaForm(BaseRihoForm):
    class Meta:
        model = Matricula
        fields = ["alumno", "grado", "ciclo_escolar", "estado"]

    def __init__(self, *args, **kwargs):
        establecimiento_id = kwargs.pop("establecimiento_id", None)
        carrera_id = kwargs.pop("carrera_id", None)
        super().__init__(*args, **kwargs)
        alumnos = Empleado.objects.all()
        grados = Grado.objects.select_related("carrera", "carrera__establecimiento")
        ciclos = CicloEscolar.objects.select_related("establecimiento")
        if establecimiento_id:
            alumnos = alumnos.filter(establecimiento_id=establecimiento_id)
            grados = grados.filter(carrera__establecimiento_id=establecimiento_id)
            ciclos = ciclos.filter(establecimiento_id=establecimiento_id)
        if carrera_id:
            grados = grados.filter(carrera_id=carrera_id)
        self.fields["alumno"].queryset = alumnos.order_by("apellidos", "nombres")
        self.fields["grado"].queryset = grados.order_by("nombre")
        self.fields["ciclo_escolar"].queryset = ciclos.order_by("-anio", "-id")
