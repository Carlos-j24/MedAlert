import datetime

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import (
    CaregiverProfile,
    Patient,
    Medication,
    Reminder,
    MedicationHistory,
    MedicalAppointment
)


def validar_password_fuerte(password, user_temporal=None):
    """
    Corre los validadores de contraseña de Django (longitud mínima,
    no común, no solo numérica, no similar al usuario) y traduce
    cualquier error a un serializers.ValidationError.

    Se usa tanto en el registro como al restablecer la contraseña
    olvidada, para no duplicar esta lógica en dos lugares.
    """

    try:
        validate_password(password, user=user_temporal)
    except DjangoValidationError as e:
        raise serializers.ValidationError(list(e.messages))

    return password


# =====================================
# PACIENTES
# =====================================

class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = [
            'id',
            'cuidador',
            'nombres',
            'apellidos',
            'identificacion',
            'genero',
            'created_at',
        ]
        read_only_fields = ['cuidador']


# =====================================
# MEDICAMENTOS
# =====================================

class MedicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medication
        fields = [
            'id',
            'patient',
            'nombre',
            'dosis',
            'descripcion',
            'frecuencia_horas',
            'duracion_cantidad',
            'duracion_unidad',
            'hora_inicio',
            'frecuencia',
            'fecha_fin',
            'activo',
            'created_at',
        ]
        read_only_fields = ['frecuencia', 'fecha_fin']

    def _texto_frecuencia(self, frecuencia_horas):

        return dict(Medication._meta.get_field('frecuencia_horas').choices)[
            frecuencia_horas
        ]

    def _calcular_fecha_fin(self, duracion_cantidad, duracion_unidad, desde=None):

        desde = desde or timezone.localdate()

        if duracion_unidad == 'meses':
            dias = duracion_cantidad * 30
        else:
            dias = duracion_cantidad

        return desde + datetime.timedelta(days=dias)

    def _generar_recordatorios(self, medication):

        veces_por_dia = 24 // medication.frecuencia_horas

        hora_inicio = medication.hora_inicio

        # Defensivo: si por alguna razón llega como texto en vez de
        # datetime.time, lo convertimos antes de combinarlo.
        if isinstance(hora_inicio, str):

            hora_inicio = datetime.datetime.strptime(
                hora_inicio, '%H:%M:%S'
            ).time()

        hora_actual = datetime.datetime.combine(
            timezone.localdate(),
            hora_inicio
        )

        for _ in range(veces_por_dia):

            Reminder.objects.create(
                patient=medication.patient,
                medication=medication,
                hora=hora_actual.time(),
                frecuencia=medication.frecuencia,
                fecha_fin=medication.fecha_fin,
            )

            hora_actual += datetime.timedelta(
                hours=medication.frecuencia_horas
            )

    def create(self, validated_data):

        # Si el cliente no envía estos campos, usamos los mismos
        # valores por defecto que tiene el modelo (validated_data
        # no los incluye automáticamente si vienen omitidos).
        frecuencia_horas = validated_data.get('frecuencia_horas', 8)
        duracion_cantidad = validated_data.get('duracion_cantidad', 7)
        duracion_unidad = validated_data.get('duracion_unidad', 'dias')

        validated_data['frecuencia'] = self._texto_frecuencia(
            frecuencia_horas
        )

        validated_data['fecha_fin'] = self._calcular_fecha_fin(
            duracion_cantidad,
            duracion_unidad,
        )

        medication = Medication.objects.create(**validated_data)

        self._generar_recordatorios(medication)

        return medication

    def update(self, instance, validated_data):

        if 'frecuencia_horas' in validated_data:

            validated_data['frecuencia'] = self._texto_frecuencia(
                validated_data['frecuencia_horas']
            )

        if 'duracion_cantidad' in validated_data or 'duracion_unidad' in validated_data:

            validated_data['fecha_fin'] = self._calcular_fecha_fin(
                validated_data.get(
                    'duracion_cantidad', instance.duracion_cantidad
                ),
                validated_data.get(
                    'duracion_unidad', instance.duracion_unidad
                ),
                desde=timezone.localdate(instance.created_at),
            )

        return super().update(instance, validated_data)


# =====================================
# RECORDATORIOS
# =====================================

class ReminderSerializer(serializers.ModelSerializer):

    medication_nombre = serializers.SerializerMethodField()

    appointment_info = serializers.SerializerMethodField()

    class Meta:
        model = Reminder
        fields = [
            'id',
            'patient',
            'medication',
            'medication_nombre',
            'appointment',
            'appointment_info',
            'fecha',
            'hora',
            'frecuencia',
            'fecha_fin',
            'activo',
            'tomado',
            'created_at',
        ]

    def get_medication_nombre(self, obj):

        if obj.medication_id:
            return obj.medication.nombre

        return None

    def get_appointment_info(self, obj):

        if obj.appointment_id:

            cita = obj.appointment

            return f"{cita.doctor} - {cita.especialidad}"

        return None


# =====================================
# HISTORIAL
# =====================================

class MedicationHistorySerializer(serializers.ModelSerializer):

    medication_nombre = serializers.CharField(
        source='medication.nombre',
        read_only=True
    )

    class Meta:
        model = MedicationHistory

        fields = [
            'id',
            'patient',
            'medication',
            'medication_nombre',
            'reminder',
            'tomado_en',
        ]

        read_only_fields = [
            'tomado_en'
        ]

# =====================================
# CITAS MÉDICAS
# =====================================

class MedicalAppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalAppointment
        fields = [
            'id',
            'patient',
            'tipo',
            'fecha',
            'hora',
            'lugar',
            'direccion',
            'barrio',
            'piso',
            'consultorio',
            'doctor',
            'especialidad',
            'estado',
            'recordatorio',
            'recordatorio_antes_cantidad',
            'recordatorio_antes_unidad',
            'created_at',
        ]

    def _generar_recordatorios(self, appointment):

        fecha_hora_cita = datetime.datetime.combine(
            appointment.fecha,
            appointment.hora
        )

        if appointment.recordatorio_antes_unidad == 'horas':

            delta = datetime.timedelta(
                hours=appointment.recordatorio_antes_cantidad
            )

        else:

            delta = datetime.timedelta(
                days=appointment.recordatorio_antes_cantidad
            )

        fecha_hora_antes = fecha_hora_cita - delta

        # Recordatorio anticipado
        Reminder.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            fecha=fecha_hora_antes.date(),
            hora=fecha_hora_antes.time(),
            frecuencia='Antes de la cita',
        )

        # Recordatorio el mismo día de la cita
        Reminder.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            fecha=appointment.fecha,
            hora=appointment.hora,
            frecuencia='Día de la cita',
        )

    def create(self, validated_data):

        appointment = MedicalAppointment.objects.create(**validated_data)

        if appointment.recordatorio:

            self._generar_recordatorios(appointment)

        return appointment


# =====================================
# REGISTRO (CUIDADOR)
# =====================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    first_name = serializers.CharField(
        required=True
    )

    last_name = serializers.CharField(
        required=True
    )

    identificacion = serializers.CharField(
        write_only=True,
        required=True
    )

    genero = serializers.ChoiceField(
        choices=CaregiverProfile._meta.get_field('genero').choices,
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'identificacion',
            'genero',
        ]

    def validate_password(self, value):

        # Construimos un User temporal (sin guardar) para que los
        # validadores puedan comparar la contraseña contra el
        # username/email, tal como exige UserAttributeSimilarityValidator.
        temp_user = User(
            username=self.initial_data.get('username', ''),
            email=self.initial_data.get('email', '')
        )

        return validar_password_fuerte(value, temp_user)

    def create(self, validated_data):

        identificacion = validated_data.pop('identificacion')
        genero = validated_data.pop('genero')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        CaregiverProfile.objects.create(
            user=user,
            identificacion=identificacion,
            genero=genero,
        )

        return user
