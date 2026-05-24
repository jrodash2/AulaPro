from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0003_carrera_ciclo_escolar'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carrera',
            options={'ordering': ['ciclo_escolar__establecimiento__nombre', 'ciclo_escolar__anio', 'nombre']},
        ),
    ]
