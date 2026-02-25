from django.db import migrations, models
from django.db.models import Q


def ensure_single_active_cycle(apps, schema_editor):
    CicloEscolar = apps.get_model('empleados_app', 'CicloEscolar')

    establecimiento_ids = (
        CicloEscolar.objects.values_list('establecimiento_id', flat=True)
        .distinct()
    )

    for est_id in establecimiento_ids:
        activos = CicloEscolar.objects.filter(establecimiento_id=est_id, es_activo=True).order_by('-id')
        keep = activos.first()
        if keep:
            activos.exclude(pk=keep.pk).update(es_activo=False)


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0019_alter_empleado_table'),
    ]

    operations = [
        migrations.RunPython(ensure_single_active_cycle, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='cicloescolar',
            name='uq_ciclo_activo_por_establecimiento',
        ),
        migrations.AddConstraint(
            model_name='cicloescolar',
            constraint=models.UniqueConstraint(
                fields=('establecimiento',),
                condition=Q(('es_activo', True)),
                name='uq_ciclo_activo_por_establecimiento',
            ),
        ),
    ]
