from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0013_alter_medication_hora_inicio'),
    ]

    operations = [

        migrations.AddField(
            model_name='caregiverprofile',
            name='whatsapp_numero',
            field=models.CharField(blank=True, max_length=20),
        ),

        migrations.AddField(
            model_name='caregiverprofile',
            name='whatsapp_apikey',
            field=models.CharField(blank=True, max_length=50),
        ),

        migrations.AddField(
            model_name='reminder',
            name='ultima_notificacion',
            field=models.DateTimeField(blank=True, null=True),
        ),

    ]
