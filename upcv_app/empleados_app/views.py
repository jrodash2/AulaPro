from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmpleadoForm, EmpleadoEditForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Empleado
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login as auth_login  
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .models import ConfiguracionGeneral
from .forms import ConfiguracionGeneralForm
from django.urls import reverse


from PIL import Image
from io import BytesIO
from django.template.loader import render_to_string



import qrcode


from django.http import HttpResponse
from django.core.files.base import ContentFile

def configuracion_general(request):
    configuracion, created = ConfiguracionGeneral.objects.get_or_create(id=1)  # Solo una configuración general
    if request.method == 'POST':
        form = ConfiguracionGeneralForm(request.POST, request.FILES, instance=configuracion)
        if form.is_valid():
            form.save()
            return redirect('empleados:configuracion_general')  # Redirige al formulario para ver los cambios
    else:
        form = ConfiguracionGeneralForm(instance=configuracion)
    
    return render(request, 'empleados/configuracion_general.html', {'form': form, 'configuracion': configuracion})

def home(request):
    return render(request, 'empleados/login.html')

@login_required 
def dahsboard(request):
    return render(request, 'empleados/dahsboard.html')


def signout(request):
    logout(request)
    return redirect('empleados:signin')

def signin(request):  
    if request.method == 'GET':
        return render(request, 'empleados/login.html', {
            'form': AuthenticationForm
        })
    else:
       
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password']
        )
        if user is None:
            return render(request, 'empleados/login.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o Password es Incorrecto'
            })
        else:
            
            auth_login(request, user)  
                      
            data = user.groups.all()
            for g in data:
                print(g.name)
                if g.name == 'Admin_gafetes':
                    return redirect('empleados:dahsboard')
                elif g.name == 'Admin_tickets':
                    return redirect('tickets:tickets_dahsboard_adm')
                elif g.name == 'tecnico':
                    return redirect('tickets:tickets_dahsboard')
                else:
                    return redirect('dahsboard')


from .models import Grado
from django.shortcuts import redirect

@login_required
def crear_empleado(request):
    grados = Grado.objects.all()  # Traemos todos los grados
    grado_descripcion = None

    # Si el formulario es enviado
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            empleado = form.save(commit=False)  # No guardes aún en la base de datos
            empleado.user = request.user  # Asigna el usuario actual
            empleado.save()  # Ahora sí guardas el objeto
            return redirect('empleados:empleado_lista')  # Redirigir a otra vista, por ejemplo, una página de éxito
    else:
        form = EmpleadoForm()

    # Pasamos el formulario y los grados a la plantilla
    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'grados': grados,  # Pasamos todos los grados
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import EmpleadoEditForm
from .models import Empleado, Grado

@login_required
def editar_empleado(request, e_id):
    # Obtener el objeto empleado a editar
    empleado = get_object_or_404(Empleado, pk=e_id)
    
    # Traer todos los grados disponibles
    grados = Grado.objects.all()

    # Si se envió el formulario
    if request.method == 'POST':
        form = EmpleadoEditForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()  # Guardar los cambios en el empleado
            return redirect('empleados:empleado_lista')  # Redirigir a la lista de empleados
        else:
            print("Errores en el formulario:", form.errors)  # Esto te permitirá ver los errores
    else:
        form = EmpleadoEditForm(instance=empleado)

    # Pasar los grados y el formulario a la plantilla
    return render(request, 'empleados/editar_empleado.html', {
        'form': form,
        'grados': grados,  # Pasamos todos los grados
        'empleado': empleado  # Para mostrar los datos actuales en la plantilla
    })




@login_required
def lista_empleados(request):
    empleados = Empleado.objects.all().order_by('-created_at', '-grado')  # Ordena por fecha de creación y luego por grado
    return render(request, 'empleados/lista_empleados.html', {'empleados': empleados})

@login_required 
def credencial_empleados(request):
    empleados = Empleado.objects.all()  
    return render(request, 'empleados/credencial_empleados.html', {'empleados': empleados})


def empleado_detalle(request, id):
    empleado = Empleado.objects.get(id=id)
    



    # Crear un archivo temporal en la memoria

    configuracion = ConfiguracionGeneral.objects.first()
    return render(request, 'empleados/empleado_detalle.html', {
        'empleado': empleado,
        'configuracion': configuracion,
    })