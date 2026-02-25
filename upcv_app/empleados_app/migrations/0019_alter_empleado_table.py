from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0018_alter_matricula_options_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterModelTable(
                    name='empleado',
                    table='empleados_app_alumno',
                ),
            ],
        ),
    ]
