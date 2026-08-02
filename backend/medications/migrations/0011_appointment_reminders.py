import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0010_medication_scheduling_fields'),
    ]

    operations = [

        migrations.AlterField(
            model_name='reminder',
            name='medication',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='medications.medication',
            ),
        ),

        migrations.AddField(
            model_name='reminder',
            name='appointment',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reminders',
                to='medications.medicalappointment',
            ),
        ),

        migrations.AddField(
            model_name='reminder',
            name='fecha',
            field=models.DateField(blank=True, null=True),
        ),

        migrations.AddField(
            model_name='medicalappointment',
            name='recordatorio_antes_cantidad',
            field=models.PositiveIntegerField(default=1),
        ),

        migrations.AddField(
            model_name='medicalappointment',
            name='recordatorio_antes_unidad',
            field=models.CharField(
                choices=[('horas', 'Horas'), ('dias', 'Días')],
                default='dias',
                max_length=10,
            ),
        ),

    ]
