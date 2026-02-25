from django import forms
from django.contrib.auth.models import User, Group
from .models import Ticket, TipoEquipo
from django.core.exceptions import ValidationError

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['oficina', 'via_contacto', 'telefono', 'correo', 'prioridad', 'tipo_equipo', 'problema', 'responsable', 'tecnico_asignado', 'estado']

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        
        # Filtrar usuarios por grupo 'tecnico'
        try:
            tecnicos_group = Group.objects.get(name='tecnico')
            self.fields['tecnico_asignado'].queryset = User.objects.filter(groups=tecnicos_group)
        except Group.DoesNotExist:
            self.fields['tecnico_asignado'].queryset = User.objects.none()
        
        # Agregar la clase 'form-control' a todos los campos del formulario
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'



            
class TickettecForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['detalle_problema', 'solucion_problema', 'estado']

    def __init__(self, *args, **kwargs):
        super(TickettecForm, self).__init__(*args, **kwargs)
        

       
        
         # Filtrar estados
        ESTADOS_PERMITIDOS = ['en_proceso', 'cerrado', 'pendiente']
        self.fields['estado'].choices = [(key, value) for key, value in self.fields['estado'].choices if key in ESTADOS_PERMITIDOS]
        # Agregar la clase 'form-control' a todos los campos del formulario
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'


from .models import Oficina

class OficinaForm(forms.ModelForm):
    class Meta:
        model = Oficina
        fields = ['nombre']

        
    def __init__(self, *args, **kwargs):
        super(OficinaForm, self).__init__(*args, **kwargs)
        
        
        # Agregar la clase 'form-control' a todos los campos del formulario
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'


class TipoEquipoForm(forms.ModelForm):
    class Meta:
        model = TipoEquipo
        fields = ['nombre']

          
    def __init__(self, *args, **kwargs):
        super(TipoEquipoForm, self).__init__(*args, **kwargs)
        
        
        # Agregar la clase 'form-control' a todos los campos del formulario
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

class UserForm(forms.ModelForm):
    new_password = forms.CharField(
        required=True, 
        widget=forms.PasswordInput, 
        label="Contraseña"
    )
    confirm_password = forms.CharField(
        required=True, 
        widget=forms.PasswordInput, 
        label="Confirmar Contraseña"
    )
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Grupo")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # No incluimos 'password' aquí

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Verificar si las contraseñas coinciden
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Si se proporciona una nueva contraseña, la seteamos
        if self.cleaned_data.get("new_password"):
            user.set_password(self.cleaned_data["new_password"])

        if commit:
            user.save()
            user.groups.add(self.cleaned_data['group'])

        return user
 
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        
        
        # Agregar la clase 'form-control' a todos los campos del formulario
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
     