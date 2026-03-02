from django.db import migrations, models
import django.db.models.deletion


def forwards_assign_cycle(apps, schema_editor):
    Carrera = apps.get_model('empleados_app', 'Carrera')
    CicloEscolar = apps.get_model('empleados_app', 'CicloEscolar')

    for carrera in Carrera.objects.all().iterator():
        ciclo = (
            CicloEscolar.objects.filter(establecimiento_id=carrera.establecimiento_id)
            .order_by('-es_activo', '-anio', '-id')
            .first()
        )
        if ciclo:
            carrera.ciclo_escolar_id = ciclo.id
            carrera.save(update_fields=['ciclo_escolar'])


def backwards_assign_establecimiento(apps, schema_editor):
    Carrera = apps.get_model('empleados_app', 'Carrera')
    for carrera in Carrera.objects.all().iterator():
        if carrera.ciclo_escolar_id:
            ciclo = carrera.ciclo_escolar
            carrera.establecimiento_id = ciclo.establecimiento_id
            carrera.save(update_fields=['establecimiento'])


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0002_configuraciongeneral_establecimiento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrera',
            name='ciclo_escolar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carreras', to='empleados_app.cicloescolar'),
        ),
        migrations.RunPython(forwards_assign_cycle, backwards_assign_establecimiento),
        migrations.AlterField(
            model_name='carrera',
            name='ciclo_escolar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carreras', to='empleados_app.cicloescolar'),
        ),
        migrations.RemoveField(
            model_name='carrera',
            name='establecimiento',
        ),
        migrations.AlterUniqueTogether(
            name='carrera',
            unique_together={('ciclo_escolar', 'nombre')},
        ),
    ]
