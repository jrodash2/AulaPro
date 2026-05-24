from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0012_observacionalumno'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracionActualizacionAlumno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habilitado', models.BooleanField(default=False)),
                ('fecha_inicio', models.DateTimeField(blank=True, null=True)),
                ('fecha_fin', models.DateTimeField(blank=True, null=True)),
                ('token_publico', models.SlugField(blank=True, max_length=120, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('establecimiento', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config_actualizacion_alumnos', to='empleados_app.establecimiento')),
            ],
            options={'ordering': ['-updated_at']},
        ),
    ]
