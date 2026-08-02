import time
import datetime

from django.core.management.base import BaseCommand

from medications.models import Reminder
from medications.whatsapp import enviar_whatsapp, WhatsAppError


class Command(BaseCommand):

    help = (
        'Revisa los recordatorios cuya hora coincide con la hora '
        'actual y envía una notificación de WhatsApp (vía CallMeBot) '
        'a los cuidadores que tengan esa opción configurada.'
    )

    def add_arguments(self, parser):

        parser.add_argument(
            '--loop',
            action='store_true',
            help='Ejecutar en bucle continuo en vez de una sola vez.',
        )

        parser.add_argument(
            '--intervalo',
            type=int,
            default=60,
            help='Segundos entre cada revisión cuando se usa --loop (por defecto 60).',
        )

    def handle(self, *args, **options):

        if options['loop']:

            self.stdout.write(
                'Revisando recordatorios cada '
                f'{options["intervalo"]} segundos. Presiona Ctrl+C para detener.'
            )

            while True:

                self._revisar()

                time.sleep(options['intervalo'])

        else:

            self._revisar()

    def _revisar(self):

        ahora = datetime.datetime.now()
        hoy = ahora.date()

        recordatorios = Reminder.objects.filter(
            activo=True,
            hora__hour=ahora.hour,
            hora__minute=ahora.minute,
        ).exclude(
            ultima_notificacion__date=hoy
        ).select_related(
            'patient__cuidador__caregiver_profile',
            'medication',
            'appointment',
        )

        for recordatorio in recordatorios:

            # Medicamento: solo si el tratamiento sigue vigente.
            if recordatorio.medication_id and recordatorio.fecha_fin:

                if recordatorio.fecha_fin < hoy:
                    continue

            # Cita: solo el día exacto para el que se generó.
            if recordatorio.appointment_id and recordatorio.fecha:

                if recordatorio.fecha != hoy:
                    continue

            self._notificar(recordatorio, ahora)

    def _notificar(self, recordatorio, ahora):

        cuidador = recordatorio.patient.cuidador

        perfil = getattr(cuidador, 'caregiver_profile', None)

        if not perfil or not perfil.whatsapp_numero or not perfil.whatsapp_apikey:
            return

        mensaje = self._mensaje(recordatorio)

        try:

            enviar_whatsapp(
                perfil.whatsapp_numero,
                perfil.whatsapp_apikey,
                mensaje,
            )

            recordatorio.ultima_notificacion = ahora

            recordatorio.save(
                update_fields=['ultima_notificacion']
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Enviado a {cuidador.username}: {mensaje}'
                )
            )

        except WhatsAppError as e:

            self.stdout.write(
                self.style.ERROR(
                    f'Error enviando a {cuidador.username}: {e}'
                )
            )

    def _mensaje(self, recordatorio):

        paciente_nombre = recordatorio.patient.nombres

        if recordatorio.medication_id:

            medicamento = recordatorio.medication

            return (
                f'💊 MedAlert: es hora de que {paciente_nombre} '
                f'tome {medicamento.nombre} ({medicamento.dosis}).'
            )

        cita = recordatorio.appointment

        return (
            f'🏥 MedAlert: recordatorio de cita para {paciente_nombre} '
            f'con {cita.doctor} ({cita.especialidad}) '
            f'el {cita.fecha.strftime("%d/%m/%Y")} '
            f'a las {cita.hora.strftime("%H:%M")}.'
        )
