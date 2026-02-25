from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from empleados_app import views as empleados_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', empleados_views.signin),
    path('logout/', empleados_views.signout),
    path('aulapro/', include('empleados_app.urls')),
    path('aulapro/', include(('empleados_app.urls', 'alumnos'), namespace='alumnos')),
    path('', RedirectView.as_view(url='/aulapro/signin/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
