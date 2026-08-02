from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0009_remove_user_require_patient'),
    ]

    operations = [

        migrations.AddField(
            model_name='medication',
            name='frecuencia_horas',
            field=models.IntegerField(
                choices=[(8, 'Cada 8 horas'), (12, 'Cada 12 horas'), (24, 'Cada 24 horas')],
                default=8,
            ),
        ),

        migrations.AddField(
            model_name='medication',
            name='duracion_cantidad',
            field=models.PositiveIntegerField(default=7),
        ),

        migrations.AddField(
            model_name='medication',
            name='duracion_unidad',
            field=models.CharField(
                choices=[('dias', 'Días'), ('meses', 'Meses')],
                default='dias',
                max_length=10,
            ),
        ),

        migrations.AddField(
            model_name='medication',
            name='hora_inicio',
            field=models.TimeField(default='08:00:00'),
        ),

        migrations.AlterField(
            model_name='medication',
            name='frecuencia',
            field=models.CharField(blank=True, max_length=100),
        ),

        migrations.AddField(
            model_name='reminder',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True),
        ),

    ]
