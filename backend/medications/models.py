from datetime import time

from django.db import models
from django.contrib.auth.models import User


GENERO_CHOICES = [

    ('masculino', 'Masculino'),

    ('femenino', 'Femenino'),

    ('prefiero_no_decir', 'Prefiero no decir'),

]


class CaregiverProfile(models.Model):
    """
    Datos adicionales del cuidador (quien inicia sesión), más allá
    de lo que ya trae el User de Django (username, email, nombres).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='caregiver_profile'
    )

    identificacion = models.CharField(max_length=50)

    genero = models.CharField(
        max_length=20,
        choices=GENERO_CHOICES,
    )

    # Configuración para notificaciones por WhatsApp (vía CallMeBot).
    # Ambos quedan vacíos hasta que el cuidador los configure.
    whatsapp_numero = models.CharField(max_length=20, blank=True)

    whatsapp_apikey = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Patient(models.Model):
    """
    Un paciente registrado por un cuidador. El paciente NO tiene
    su propio login: toda la gestión ocurre desde la cuenta del
    cuidador.
    """

    cuidador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patients'
    )

    nombres = models.CharField(max_length=150)

    apellidos = models.CharField(max_length=150)

    identificacion = models.CharField(max_length=50)

    genero = models.CharField(
        max_length=20,
        choices=GENERO_CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


FRECUENCIA_HORAS_CHOICES = [

    (8, 'Cada 8 horas'),

    (12, 'Cada 12 horas'),

    (24, 'Cada 24 horas'),

]

DURACION_UNIDAD_CHOICES = [

    ('dias', 'Días'),

    ('meses', 'Meses'),

]

ANTES_UNIDAD_CHOICES = [

    ('horas', 'Horas'),

    ('dias', 'Días'),

]


class Medication(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medications'
    )

    nombre = models.CharField(max_length=255)

    dosis = models.CharField(max_length=100)

    descripcion = models.TextField(blank=True)

    # Cada cuántas horas se debe tomar (usado para generar los
    # recordatorios automáticamente).
    frecuencia_horas = models.IntegerField(
        choices=FRECUENCIA_HORAS_CHOICES,
        default=8,
    )

    # Cuánto dura el tratamiento.
    duracion_cantidad = models.PositiveIntegerField(default=7)

    duracion_unidad = models.CharField(
        max_length=10,
        choices=DURACION_UNIDAD_CHOICES,
        default='dias',
    )

    # Hora de la primera toma del día, usada como punto de partida
    # para calcular las horas de los recordatorios.
    hora_inicio = models.TimeField(default=time(8, 0))

    # Fecha en la que termina el tratamiento, calculada una sola
    # vez al crear el medicamento (created_at + duración). Vive
    # aquí directamente para no depender de que existan
    # recordatorios asociados.
    fecha_fin = models.DateField(null=True, blank=True)

    # Texto legible calculado automáticamente (ej. "Cada 8 horas"),
    # se recalcula solo, no se edita directamente.
    frecuencia = models.CharField(max_length=100, blank=True)

    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Reminder(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='reminders'
    )

    # Un recordatorio pertenece A UNO de los dos: un medicamento
    # (se repite todos los días) o una cita médica (fecha puntual).
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    appointment = models.ForeignKey(
        'MedicalAppointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reminders',
    )

    # Fecha puntual del recordatorio. Solo aplica a recordatorios de
    # citas médicas (un evento único). Los recordatorios de
    # medicamentos se repiten a diario y no usan este campo.
    fecha = models.DateField(null=True, blank=True)

    hora = models.TimeField()

    frecuencia = models.CharField(max_length=100)

    # Fecha en la que el tratamiento termina y el recordatorio deja
    # de ser relevante. Nulo para recordatorios creados a mano
    # (sin fecha de fin definida).
    fecha_fin = models.DateField(null=True, blank=True)

    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    tomado = models.BooleanField(default=False)

    # Cuándo se envió por última vez una notificación (WhatsApp,
    # etc.) para este recordatorio. Evita reenviar el mismo aviso
    # varias veces el mismo día.
    ultima_notificacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):

        if self.medication_id:
            return f"{self.medication.nombre} - {self.hora}"

        return f"Cita {self.appointment_id} - {self.hora}"


class MedicationHistory(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='history'
    )

    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE
    )

    reminder = models.ForeignKey(
        'Reminder',
        on_delete=models.CASCADE
    )

    tomado_en = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.medication.nombre} - {self.patient.nombres}"


class MedicalAppointment(models.Model):

    STATUS_CHOICES = [

        ('pendiente', 'Pendiente'),

        ('cumplida', 'Cumplida'),

        ('cancelada', 'Cancelada'),

    ]

    TIPO_CHOICES = [

        ('consulta', 'Consulta con especialista'),

        ('examen', 'Examen médico'),

        ('terapia', 'Terapia física'),

        ('cirugia', 'Cirugía programada'),

    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='consulta',
    )

    fecha = models.DateField()

    hora = models.TimeField()

    lugar = models.CharField(
        max_length=255
    )

    direccion = models.CharField(
        max_length=255
    )

    barrio = models.CharField(
        max_length=255
    )

    piso = models.CharField(
        max_length=50
    )

    consultorio = models.CharField(
        max_length=50
    )

    doctor = models.CharField(
        max_length=255
    )

    especialidad = models.CharField(
        max_length=255
    )

    estado = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='pendiente'

    )

    recordatorio = models.BooleanField(
        default=True
    )

    # Cuánto tiempo antes de la cita se genera el primer
    # recordatorio (el segundo siempre es el mismo día de la cita).
    recordatorio_antes_cantidad = models.PositiveIntegerField(
        default=1
    )

    recordatorio_antes_unidad = models.CharField(
        max_length=10,
        choices=ANTES_UNIDAD_CHOICES,
        default='dias',
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.doctor} - {self.fecha}"
