import datetime

from django.db import migrations, models


def calcular_fecha_fin_existentes(apps, schema_editor):

    Medication = apps.get_model('medications', 'Medication')

    for medicamento in Medication.objects.all():

        if medicamento.duracion_unidad == 'meses':
            dias = medicamento.duracion_cantidad * 30
        else:
            dias = medicamento.duracion_cantidad

        medicamento.fecha_fin = (
            medicamento.created_at.date() + datetime.timedelta(days=dias)
        )

        medicamento.save(update_fields=['fecha_fin'])


def revertir(apps, schema_editor):
    # No-op: al revertir simplemente se pierde el valor calculado,
    # no hace falta deshacer nada explícitamente.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0011_appointment_reminders'),
    ]

    operations = [

        migrations.AddField(
            model_name='medication',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True),
        ),

        migrations.AddField(
            model_name='medicalappointment',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('consulta', 'Consulta con especialista'),
                    ('examen', 'Examen médico'),
                    ('terapia', 'Terapia física'),
                    ('cirugia', 'Cirugía programada'),
                ],
                default='consulta',
                max_length=20,
            ),
        ),

        migrations.RunPython(
            calcular_fecha_fin_existentes,
            revertir
        ),

    ]
