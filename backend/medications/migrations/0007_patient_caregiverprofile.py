import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0006_medicalappointment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        migrations.CreateModel(
            name='CaregiverProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identificacion', models.CharField(max_length=50)),
                ('genero', models.CharField(choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('prefiero_no_decir', 'Prefiero no decir')], max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='caregiver_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),

        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombres', models.CharField(max_length=150)),
                ('apellidos', models.CharField(max_length=150)),
                ('identificacion', models.CharField(max_length=50)),
                ('genero', models.CharField(choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('prefiero_no_decir', 'Prefiero no decir')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cuidador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patients', to=settings.AUTH_USER_MODEL)),
            ],
        ),

        migrations.AddField(
            model_name='medication',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='medications.patient'),
        ),

        migrations.AddField(
            model_name='reminder',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='medications.patient'),
        ),

        migrations.AddField(
            model_name='medicationhistory',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history', to='medications.patient'),
        ),

        migrations.AddField(
            model_name='medicalappointment',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='medications.patient'),
        ),

    ]
