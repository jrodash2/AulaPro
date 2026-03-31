from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

from .models import Carrera, CicloEscolar, ConfiguracionGeneral, Curso, CursoDocente, Empleado, Establecimiento, Grado, Matricula, ObservacionAlumno, Perfil
from .permissions import es_gestor, obtener_establecimiento_usuario


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
            "imagen",
            "tel",
            "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["imagen"].widget.attrs.update({
            "accept": "image/*",
            "capture": "user",
        })


class EmpleadoEditForm(EmpleadoForm):
    pass


class EstablecimientoForm(BaseRihoForm):
    ORIENTACION_CHOICES = (("H", "Horizontal (1011x639)"), ("V", "Vertical (639x1011)"))
    gafete_orientacion = forms.ChoiceField(choices=ORIENTACION_CHOICES)

    class Meta:
        model = Establecimiento
        fields = ["nombre", "direccion", "sitio_web", "background_gafete", "background_gafete_posterior", "gafete_orientacion", "gafete_ancho", "gafete_alto", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        orientacion = "V" if (self.instance and self.instance.gafete_alto > self.instance.gafete_ancho) else "H"
        self.fields["gafete_orientacion"].initial = orientacion
        self.fields["gafete_ancho"].widget.attrs["readonly"] = True
        self.fields["gafete_alto"].widget.attrs["readonly"] = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        orientacion = self.cleaned_data.get("gafete_orientacion", "H")
        if orientacion == "V":
            instance.gafete_ancho, instance.gafete_alto = 639, 1011
        else:
            instance.gafete_ancho, instance.gafete_alto = 1011, 639
        if commit:
            instance.save()
        return instance


class CarreraForm(BaseRihoForm):
    class Meta:
        model = Carrera
        fields = ["nombre", "activo"]


class GradoForm(BaseRihoForm):
    class Meta:
        model = Grado
        fields = ["nombre", "descripcion", "jornada", "seccion", "activo"]


class CicloEscolarForm(BaseRihoForm):
    DATE_INPUT_FORMATS = ["%d/%m/%Y", "%Y-%m-%d"]

    fecha_inicio = forms.DateField(
        required=False,
        input_formats=DATE_INPUT_FORMATS,
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "placeholder": "dd/mm/aaaa",
                "autocomplete": "off",
            },
        ),
    )
    fecha_fin = forms.DateField(
        required=False,
        input_formats=DATE_INPUT_FORMATS,
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "placeholder": "dd/mm/aaaa",
                "autocomplete": "off",
            },
        ),
    )

    class Meta:
        model = CicloEscolar
        fields = ["nombre", "anio", "fecha_inicio", "fecha_fin", "activo"]

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre:
            raise forms.ValidationError("El nombre del ciclo escolar es obligatorio.")
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error("fecha_fin", "La fecha fin no puede ser menor que la fecha inicio.")
        return cleaned_data


class MatriculaForm(BaseRihoForm):
    class Meta:
        model = Matricula
        fields = ["alumno", "grado", "ciclo_escolar", "estado"]

    def __init__(self, *args, **kwargs):
        establecimiento_id = kwargs.pop("establecimiento_id", None)
        carrera_id = kwargs.pop("carrera_id", None)
        super().__init__(*args, **kwargs)
        alumnos = Empleado.objects.all()
        grados = Grado.objects.select_related("carrera", "carrera__ciclo_escolar", "carrera__ciclo_escolar__establecimiento")
        ciclos = CicloEscolar.objects.select_related("establecimiento")
        if establecimiento_id:
            grados = grados.filter(carrera__ciclo_escolar__establecimiento_id=establecimiento_id)
            ciclos = ciclos.filter(establecimiento_id=establecimiento_id)
        if carrera_id:
            grados = grados.filter(carrera_id=carrera_id)
        self.fields["alumno"].queryset = alumnos.order_by("apellidos", "nombres")
        self.fields["grado"].queryset = grados.order_by("nombre")
        self.fields["ciclo_escolar"].queryset = ciclos.order_by("-anio", "-id")


class MatriculaMasivaForm(forms.Form):
    grado = forms.ModelChoiceField(queryset=Grado.objects.none(), required=True)
    ciclo_escolar = forms.ModelChoiceField(queryset=CicloEscolar.objects.none(), required=True)
    estado = forms.ChoiceField(choices=Matricula.ESTADOS, required=True, initial="activo")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        grados = Grado.objects.select_related("carrera", "carrera__ciclo_escolar", "carrera__ciclo_escolar__establecimiento")
        ciclos = CicloEscolar.objects.select_related("establecimiento")

        establecimiento_usuario = obtener_establecimiento_usuario(user)
        if establecimiento_usuario:
            grados = grados.filter(carrera__ciclo_escolar__establecimiento=establecimiento_usuario)
            ciclos = ciclos.filter(establecimiento=establecimiento_usuario)

        self.fields["grado"].queryset = grados.order_by("nombre")
        self.fields["ciclo_escolar"].queryset = ciclos.order_by("-anio", "-id")

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                current = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{current} form-control".strip()


class ObservacionAlumnoForm(BaseRihoForm):
    class Meta:
        model = ObservacionAlumno
        fields = ["fecha", "tipo", "prioridad", "estado", "observacion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "observacion": forms.Textarea(attrs={"rows": 4}),
        }


class CargaMasivaExcelForm(forms.Form):
    archivo = forms.FileField(required=True)
    confirmar = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["archivo"].widget.attrs["class"] = "form-control"
        self.fields["archivo"].widget.attrs["accept"] = ".xlsx,.xlsm"
        self.fields["confirmar"].widget.attrs["class"] = "form-check-input"


class UsuarioCreateForm(UserCreationForm):
    foto = forms.ImageField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    establecimiento_gestionado = forms.ModelChoiceField(
        queryset=Establecimiento.objects.filter(activo=True).order_by("nombre"),
        required=False,
        empty_label="Sin asignación",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "is_active", "groups", "establecimiento_gestionado", "foto")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["foto"].widget.attrs["class"] = "form-control"
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                current = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{current} form-control".strip()

    def clean(self):
        cleaned_data = super().clean()
        groups = cleaned_data.get("groups")
        establecimiento = cleaned_data.get("establecimiento_gestionado")
        if groups and any(group.name == "Gestor" for group in groups) and not establecimiento:
            self.add_error("establecimiento_gestionado", "Debe asignar un establecimiento para usuarios Gestor.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data.get("email", "")
        user.is_active = self.cleaned_data.get("is_active", True)
        if commit:
            user.save()
            user.groups.set(self.cleaned_data.get("groups"))
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.establecimiento_gestionado = self.cleaned_data.get("establecimiento_gestionado") if es_gestor(user) else None
            perfil.save(update_fields=["establecimiento_gestionado"])
        return user


class UsuarioUpdateForm(forms.ModelForm):
    foto = forms.ImageField(required=False)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    establecimiento_gestionado = forms.ModelChoiceField(
        queryset=Establecimiento.objects.filter(activo=True).order_by("nombre"),
        required=False,
        empty_label="Sin asignación",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "groups", "establecimiento_gestionado", "foto")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["foto"].widget.attrs["class"] = "form-control"
        self.fields["groups"].initial = self.instance.groups.all()
        perfil, _ = Perfil.objects.get_or_create(user=self.instance)
        self.fields["establecimiento_gestionado"].initial = perfil.establecimiento_gestionado
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                current = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{current} form-control".strip()

    def clean(self):
        cleaned_data = super().clean()
        groups = cleaned_data.get("groups")
        establecimiento = cleaned_data.get("establecimiento_gestionado")
        if groups and any(group.name == "Gestor" for group in groups) and not establecimiento:
            self.add_error("establecimiento_gestionado", "Debe asignar un establecimiento para usuarios Gestor.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.set(self.cleaned_data.get("groups"))
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.establecimiento_gestionado = self.cleaned_data.get("establecimiento_gestionado") if es_gestor(user) else None
            perfil.save(update_fields=["establecimiento_gestionado"])
        return user


class CursoForm(BaseRihoForm):
    class Meta:
        model = Curso
        fields = ["nombre", "descripcion", "activo"]


class AsignarDocenteForm(forms.Form):
    docente = forms.ModelChoiceField(queryset=User.objects.none(), required=True)
    activo = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["docente"].queryset = User.objects.filter(groups__name="Docente").order_by("first_name", "last_name", "username").distinct()
        self.fields["docente"].widget.attrs["class"] = "form-control"
        self.fields["activo"].widget.attrs["class"] = "form-check-input"

    def save(self, curso):
        docente = self.cleaned_data["docente"]
        activo = self.cleaned_data.get("activo", True)
        asignacion, _ = CursoDocente.objects.get_or_create(curso=curso, docente=docente)
        asignacion.activo = activo
        asignacion.full_clean()
        asignacion.save()
        return asignacion
