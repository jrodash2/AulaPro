from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("empleados_app", "0020_fix_ciclo_activo_constraint"),
    ]

    operations = [
        migrations.AddField(
            model_name="establecimiento",
            name="sitio_web",
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
