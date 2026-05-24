from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empleados_app', '0010_perfil_establecimiento_gestor_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='establecimiento',
            name='background_gafete_posterior',
            field=models.ImageField(blank=True, null=True, upload_to='logotipos2/'),
        ),
    ]
