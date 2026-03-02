from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0004_alter_carrera_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cicloescolar',
            old_name='es_activo',
            new_name='activo',
        ),
        migrations.RemoveField(
            model_name='cicloescolar',
            name='estado',
        ),
        migrations.RemoveIndex(
            model_name='cicloescolar',
            name='empleados_a_estable_ff9faa_idx',
        ),
        migrations.AddIndex(
            model_name='cicloescolar',
            index=models.Index(fields=['establecimiento', 'activo'], name='empleados_a_estable_fe504c_idx'),
        ),
        migrations.RemoveConstraint(
            model_name='cicloescolar',
            name='uq_ciclo_activo_por_establecimiento',
        ),
        migrations.AddConstraint(
            model_name='cicloescolar',
            constraint=models.UniqueConstraint(condition=Q(activo=True), fields=('establecimiento',), name='uq_ciclo_activo_por_establecimiento'),
        ),
    ]
