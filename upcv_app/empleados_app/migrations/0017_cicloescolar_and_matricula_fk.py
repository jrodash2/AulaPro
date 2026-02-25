from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


def migrate_ciclos_from_matricula(apps, schema_editor):
    Establecimiento = apps.get_model('empleados_app', 'Establecimiento')
    CicloEscolar = apps.get_model('empleados_app', 'CicloEscolar')
    Matricula = apps.get_model('empleados_app', 'Matricula')

    for matricula in Matricula.objects.filter(ciclo_escolar__isnull=True).select_related('grado', 'grado__carrera', 'grado__carrera__establecimiento'):
        grado = matricula.grado
        if not grado or not grado.carrera or not grado.carrera.establecimiento_id:
            continue

        establecimiento = grado.carrera.establecimiento
        nombre_ciclo = str(matricula.ciclo) if matricula.ciclo else 'Sin año'
        ciclo, _ = CicloEscolar.objects.get_or_create(
            establecimiento=establecimiento,
            nombre=nombre_ciclo,
            defaults={
                'anio': matricula.ciclo,
                'estado': 'activo',
                'es_activo': False,
            },
        )
        matricula.ciclo_escolar = ciclo
        matricula.save(update_fields=['ciclo_escolar'])

    for establecimiento in Establecimiento.objects.all():
        if establecimiento.ciclos_escolares.filter(es_activo=True).exists():
            continue
        ciclo = establecimiento.ciclos_escolares.order_by('-anio', '-id').first()
        if ciclo:
            ciclo.es_activo = True
            ciclo.estado = 'activo'
            ciclo.save(update_fields=['es_activo', 'estado'])


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0015_carrera_establecimiento_alter_empleado_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CicloEscolar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('anio', models.PositiveIntegerField(blank=True, null=True)),
                ('fecha_inicio', models.DateField(blank=True, null=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('es_activo', models.BooleanField(default=False)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=10)),
                ('establecimiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ciclos_escolares', to='empleados_app.establecimiento')),
            ],
            options={
                'ordering': ['-anio', '-id'],
            },
        ),
        migrations.AddField(
            model_name='matricula',
            name='ciclo_escolar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='matriculas', to='empleados_app.cicloescolar'),
        ),
        migrations.AlterField(
            model_name='matricula',
            name='ciclo',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_ciclos_from_matricula, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='matricula',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='cicloescolar',
            constraint=models.UniqueConstraint(fields=('establecimiento', 'nombre'), name='uq_ciclo_nombre_establecimiento'),
        ),
        migrations.AddConstraint(
            model_name='cicloescolar',
            constraint=models.UniqueConstraint(condition=Q(('es_activo', True)), fields=('establecimiento',), name='uq_ciclo_activo_por_establecimiento'),
        ),
        migrations.AddConstraint(
            model_name='matricula',
            constraint=models.UniqueConstraint(condition=Q(('ciclo_escolar__isnull', False)), fields=('alumno', 'grado', 'ciclo_escolar'), name='uq_matricula_alumno_grado_ciclo_escolar'),
        ),
        migrations.AddIndex(
            model_name='cicloescolar',
            index=models.Index(fields=['establecimiento', 'es_activo'], name='empleados_ap_estable_70f9a0_idx'),
        ),
        migrations.AddIndex(
            model_name='cicloescolar',
            index=models.Index(fields=['establecimiento', 'anio'], name='empleados_ap_estable_a4b786_idx'),
        ),
        migrations.AddIndex(
            model_name='matricula',
            index=models.Index(fields=['grado', 'estado'], name='empleados_ap_grado_958691_idx'),
        ),
        migrations.AddIndex(
            model_name='matricula',
            index=models.Index(fields=['grado', 'ciclo_escolar'], name='empleados_ap_grado_aef92f_idx'),
        ),
    ]
