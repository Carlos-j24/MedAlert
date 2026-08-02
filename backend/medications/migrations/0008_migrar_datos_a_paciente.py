from django.db import migrations


def migrar_datos_a_paciente(apps, schema_editor):

    User = apps.get_model('auth', 'User')
    CaregiverProfile = apps.get_model('medications', 'CaregiverProfile')
    Patient = apps.get_model('medications', 'Patient')
    Medication = apps.get_model('medications', 'Medication')
    Reminder = apps.get_model('medications', 'Reminder')
    MedicationHistory = apps.get_model('medications', 'MedicationHistory')
    MedicalAppointment = apps.get_model('medications', 'MedicalAppointment')

    for user in User.objects.all():

        CaregiverProfile.objects.get_or_create(
            user=user,
            defaults={
                'identificacion': f'PENDIENTE-{user.id}',
                'genero': 'prefiero_no_decir',
            }
        )

        tiene_datos = (
            Medication.objects.filter(user_id=user.id).exists()
            or Reminder.objects.filter(user_id=user.id).exists()
            or MedicationHistory.objects.filter(user_id=user.id).exists()
            or MedicalAppointment.objects.filter(user_id=user.id).exists()
        )

        if not tiene_datos:
            continue

        patient = Patient.objects.create(
            cuidador=user,
            nombres=user.first_name or user.username,
            apellidos=user.last_name or '',
            identificacion=f'PENDIENTE-{user.id}',
            genero='prefiero_no_decir',
        )

        Medication.objects.filter(user_id=user.id).update(patient=patient)
        Reminder.objects.filter(user_id=user.id).update(patient=patient)
        MedicationHistory.objects.filter(user_id=user.id).update(patient=patient)
        MedicalAppointment.objects.filter(user_id=user.id).update(patient=patient)


def revertir(apps, schema_editor):
    # No se puede revertir de forma segura (perderíamos la
    # asignación paciente -> registros). No-op intencional.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0007_patient_caregiverprofile'),
    ]

    operations = [
        migrations.RunPython(migrar_datos_a_paciente, revertir),
    ]
