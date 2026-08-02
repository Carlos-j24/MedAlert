import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0008_migrar_datos_a_paciente'),
    ]

    operations = [

        migrations.RemoveField(
            model_name='medication',
            name='user',
        ),

        migrations.RemoveField(
            model_name='reminder',
            name='user',
        ),

        migrations.RemoveField(
            model_name='medicationhistory',
            name='user',
        ),

        migrations.RemoveField(
            model_name='medicalappointment',
            name='user',
        ),

        migrations.AlterField(
            model_name='medication',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='medications.patient'),
        ),

        migrations.AlterField(
            model_name='reminder',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='medications.patient'),
        ),

        migrations.AlterField(
            model_name='medicationhistory',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='medications.patient'),
        ),

        migrations.AlterField(
            model_name='medicalappointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='medications.patient'),
        ),

    ]
