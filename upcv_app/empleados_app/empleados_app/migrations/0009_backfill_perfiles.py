from django.conf import settings
from django.db import migrations


def backfill_perfiles(apps, schema_editor):
    Perfil = apps.get_model('empleados_app', 'Perfil')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))

    for user in User.objects.iterator():
        Perfil.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0008_periodoacademico_asistencia_periodo_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(backfill_perfiles, migrations.RunPython.noop),
    ]
