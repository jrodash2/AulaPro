from django.db import migrations, models
import django.db.models.deletion


def crear_grupo_gestor(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Gestor')


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0009_backfill_perfiles'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='establecimiento_gestionado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gestores_asignados', to='empleados_app.establecimiento'),
        ),
        migrations.RunPython(crear_grupo_gestor, migrations.RunPython.noop),
    ]
