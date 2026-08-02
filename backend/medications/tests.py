import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APITestCase
from rest_framework import status

from .models import (
    Patient, Medication, Reminder, CaregiverProfile, MedicalAppointment
)


DATOS_REGISTRO_VALIDOS = {
    'username': 'nuevo_usuario',
    'email': 'nuevo@test.com',
    'password': 'ContraseñaSegura2024!',
    'first_name': 'Laura',
    'last_name': 'Pérez',
    'identificacion': '1000000001',
    'genero': 'femenino',
}


# =====================================
# REGISTRO
# =====================================

class RegisterTests(APITestCase):
    """
    Pruebas del endpoint de registro (/api/register/), incluyendo la
    validación de contraseña y los datos nuevos del cuidador.
    """

    def setUp(self):
        self.url = '/api/register/'

        # Limpiamos la caché de throttling antes de cada prueba,
        # para que el límite de 5/hora en /api/register/ no
        # interfiera entre pruebas distintas.
        cache.clear()

    def test_registro_con_datos_validos_crea_usuario(self):
        response = self.client.post(self.url, DATOS_REGISTRO_VALIDOS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        usuario = User.objects.get(username='nuevo_usuario')

        self.assertEqual(usuario.first_name, 'Laura')
        self.assertEqual(usuario.last_name, 'Pérez')
        self.assertTrue(
            hasattr(usuario, 'caregiver_profile')
        )
        self.assertEqual(
            usuario.caregiver_profile.identificacion, '1000000001'
        )

    def test_registro_sin_nombres_es_rechazado(self):
        datos = {**DATOS_REGISTRO_VALIDOS, 'username': 'otro_usuario'}
        datos.pop('first_name')

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)

    def test_registro_sin_identificacion_es_rechazado(self):
        datos = {**DATOS_REGISTRO_VALIDOS, 'username': 'otro_usuario2'}
        datos.pop('identificacion')

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('identificacion', response.data)

    def test_registro_con_genero_invalido_es_rechazado(self):
        datos = {
            **DATOS_REGISTRO_VALIDOS,
            'username': 'otro_usuario3',
            'genero': 'no_es_una_opcion_valida',
        }

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('genero', response.data)

    def test_registro_con_contrasena_muy_corta_es_rechazado(self):
        datos = {
            **DATOS_REGISTRO_VALIDOS,
            'username': 'otro_usuario4',
            'password': '123',
        }

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registro_con_username_duplicado_es_rechazado(self):
        User.objects.create_user(
            username='existente', password='ContraseñaValida2024!'
        )

        datos = {**DATOS_REGISTRO_VALIDOS, 'username': 'existente'}

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)


# =====================================
# PACIENTES
# =====================================

class PatientTests(APITestCase):
    """
    Verifica que un cuidador solo pueda ver, editar y borrar a sus
    propios pacientes, nunca a los de otro cuidador.
    """

    def setUp(self):
        self.cuidador1 = User.objects.create_user(
            username='cuidador1', password='ContraseñaValida2024!'
        )
        self.cuidador2 = User.objects.create_user(
            username='cuidador2', password='ContraseñaValida2024!'
        )

        self.paciente_de_cuidador1 = Patient.objects.create(
            cuidador=self.cuidador1,
            nombres='Ana',
            apellidos='Gómez',
            identificacion='111111',
            genero='femenino',
        )

        self.client.force_authenticate(user=self.cuidador2)

    def test_cuidador_puede_crear_su_propio_paciente(self):
        response = self.client.post('/api/patients/', {
            'nombres': 'Luis',
            'apellidos': 'Ramírez',
            'identificacion': '222222',
            'genero': 'masculino',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        paciente = Patient.objects.get(nombres='Luis')
        self.assertEqual(paciente.cuidador, self.cuidador2)

    def test_cuidador_no_ve_pacientes_de_otro_cuidador(self):
        response = self.client.get('/api/patients/')

        nombres = [p['nombres'] for p in response.data['results']]
        self.assertNotIn('Ana', nombres)

    def test_cuidador_no_puede_ver_paciente_ajeno(self):
        response = self.client.get(
            f'/api/patients/{self.paciente_de_cuidador1.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cuidador_no_puede_editar_paciente_ajeno(self):
        response = self.client.patch(
            f'/api/patients/{self.paciente_de_cuidador1.id}/',
            {'nombres': 'Hackeado'},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# =====================================
# AISLAMIENTO DE DATOS ENTRE CUIDADORES
# =====================================

class MedicationAislamientoTests(APITestCase):
    """
    Verifica que un cuidador nunca pueda ver, editar, borrar, ni
    asignar medicamentos al paciente de OTRO cuidador.
    """

    def setUp(self):
        self.cuidador1 = User.objects.create_user(
            username='cuidador1', password='ContraseñaValida2024!'
        )
        self.cuidador2 = User.objects.create_user(
            username='cuidador2', password='ContraseñaValida2024!'
        )

        self.paciente1 = Patient.objects.create(
            cuidador=self.cuidador1,
            nombres='Ana', apellidos='Gómez',
            identificacion='111111', genero='femenino',
        )

        self.paciente2 = Patient.objects.create(
            cuidador=self.cuidador2,
            nombres='Luis', apellidos='Ramírez',
            identificacion='222222', genero='masculino',
        )

        self.medicamento_paciente1 = Medication.objects.create(
            patient=self.paciente1,
            nombre='Paracetamol',
            dosis='500mg',
            frecuencia='cada 8 horas',
        )

        self.client.force_authenticate(user=self.cuidador2)

    def test_cuidador_no_ve_medicamentos_de_paciente_ajeno(self):
        response = self.client.get('/api/medications/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        nombres = [
            m['nombre'] for m in response.data['results']
        ]
        self.assertNotIn('Paracetamol', nombres)

    def test_cuidador_no_puede_ver_detalle_de_medicamento_ajeno(self):
        response = self.client.get(
            f'/api/medications/{self.medicamento_paciente1.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cuidador_no_puede_editar_medicamento_ajeno(self):
        response = self.client.patch(
            f'/api/medications/{self.medicamento_paciente1.id}/',
            {'nombre': 'Hackeado'},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.medicamento_paciente1.refresh_from_db()
        self.assertEqual(self.medicamento_paciente1.nombre, 'Paracetamol')

    def test_cuidador_no_puede_borrar_medicamento_ajeno(self):
        response = self.client.delete(
            f'/api/medications/{self.medicamento_paciente1.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Medication.objects.filter(id=self.medicamento_paciente1.id).exists()
        )

    def test_medicamento_creado_para_paciente_propio_funciona(self):
        response = self.client.post('/api/medications/', {
            'patient': self.paciente2.id,
            'nombre': 'Ibuprofeno',
            'dosis': '400mg',
            'frecuencia': 'cada 12 horas',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        medicamento = Medication.objects.get(nombre='Ibuprofeno')
        self.assertEqual(medicamento.patient, self.paciente2)

    def test_no_puede_crear_medicamento_para_paciente_ajeno(self):
        response = self.client.post('/api/medications/', {
            'patient': self.paciente1.id,
            'nombre': 'Aspirina',
            'dosis': '100mg',
            'frecuencia': 'diaria',
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Medication.objects.filter(nombre='Aspirina').exists()
        )


# =====================================
# PAGINACIÓN
# =====================================

class PaginacionTests(APITestCase):
    """
    Verifica que el listado de medicamentos venga paginado
    (10 por página por defecto) y que ?page_size permita pedir más.
    """

    def setUp(self):
        self.cuidador = User.objects.create_user(
            username='usuario_paginacion',
            password='ContraseñaValida2024!',
        )

        self.paciente = Patient.objects.create(
            cuidador=self.cuidador,
            nombres='Ana', apellidos='Gómez',
            identificacion='333333', genero='femenino',
        )

        self.client.force_authenticate(user=self.cuidador)

        for i in range(15):
            Medication.objects.create(
                patient=self.paciente,
                nombre=f'Medicamento {i}',
                dosis='500mg',
                frecuencia='diaria',
            )

    def test_listado_viene_paginado_por_defecto(self):
        response = self.client.get('/api/medications/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

        self.assertEqual(response.data['count'], 15)
        self.assertEqual(len(response.data['results']), 10)

    def test_page_size_permite_pedir_mas_resultados(self):
        response = self.client.get('/api/medications/?page_size=100')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 15)


# =====================================
# BÚSQUEDA
# =====================================

class BusquedaTests(APITestCase):
    """
    Verifica que se pueda buscar por texto en medicamentos y citas,
    y filtrar citas por tipo.
    """

    def setUp(self):

        self.cuidador = User.objects.create_user(
            username='usuario_busqueda',
            password='ContraseñaValida2024!',
        )

        self.paciente = Patient.objects.create(
            cuidador=self.cuidador,
            nombres='Ana', apellidos='Gómez',
            identificacion='777777', genero='femenino',
        )

        self.client.force_authenticate(user=self.cuidador)

        Medication.objects.create(
            patient=self.paciente,
            nombre='Paracetamol', dosis='500mg', frecuencia='diaria',
        )

        Medication.objects.create(
            patient=self.paciente,
            nombre='Ibuprofeno', dosis='400mg', frecuencia='diaria',
        )

        MedicalAppointment.objects.create(
            patient=self.paciente,
            tipo='consulta',
            fecha=datetime.date.today() + datetime.timedelta(days=5),
            hora=datetime.time(10, 0),
            lugar='Clínica Central', direccion='Calle 1', barrio='Centro',
            piso='2', consultorio='204',
            doctor='Dr. Pérez', especialidad='Cardiología',
        )

        MedicalAppointment.objects.create(
            patient=self.paciente,
            tipo='examen',
            fecha=datetime.date.today() + datetime.timedelta(days=8),
            hora=datetime.time(9, 0),
            lugar='Lab Nacional', direccion='Calle 2', barrio='Norte',
            piso='1', consultorio='101',
            doctor='Dr. Ruiz', especialidad='Laboratorio',
        )

    def test_buscar_medicamento_por_nombre(self):

        response = self.client.get('/api/medications/?search=Ibupro')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['nombre'], 'Ibuprofeno'
        )

    def test_buscar_medicamento_sin_coincidencias(self):

        response = self.client.get('/api/medications/?search=noexiste')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_buscar_cita_por_doctor(self):

        response = self.client.get('/api/appointments/?search=Pérez')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['doctor'], 'Dr. Pérez'
        )

    def test_filtrar_citas_por_tipo(self):

        response = self.client.get('/api/appointments/?tipo=examen')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['tipo'], 'examen'
        )


# =====================================
# PROTECCIÓN CONTRA FUERZA BRUTA (THROTTLING)
# =====================================

class ThrottlingTests(APITestCase):
    """
    Verifica que login y registro se bloqueen después de demasiados
    intentos seguidos desde la misma IP.
    """

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username='usuario_throttle',
            password='ContraseñaValida2024!',
        )

    def test_login_se_bloquea_tras_demasiados_intentos(self):
        for _ in range(5):

            response = self.client.post('/api/token/', {
                'username': 'usuario_throttle',
                'password': 'contraseña-incorrecta',
            })

            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS,
            )

        response = self.client.post('/api/token/', {
            'username': 'usuario_throttle',
            'password': 'contraseña-incorrecta',
        })

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    def test_registro_se_bloquea_tras_demasiados_intentos(self):
        for i in range(5):

            datos = {
                **DATOS_REGISTRO_VALIDOS,
                'username': f'usuario_nuevo_{i}',
                'email': f'nuevo_{i}@test.com',
            }

            response = self.client.post('/api/register/', datos)

            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS,
            )

        datos = {
            **DATOS_REGISTRO_VALIDOS,
            'username': 'usuario_nuevo_bloqueado',
            'email': 'bloqueado@test.com',
        }

        response = self.client.post('/api/register/', datos)

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )


# =====================================
# GENERACIÓN AUTOMÁTICA DE RECORDATORIOS
# =====================================

class GeneracionRecordatoriosTests(APITestCase):
    """
    Verifica que al crear un medicamento con una frecuencia y
    duración, se generen automáticamente los recordatorios
    correspondientes.
    """

    def setUp(self):
        self.cuidador = User.objects.create_user(
            username='cuidador_recordatorios',
            password='ContraseñaValida2024!',
        )

        self.paciente = Patient.objects.create(
            cuidador=self.cuidador,
            nombres='Ana', apellidos='Gómez',
            identificacion='444444', genero='femenino',
        )

        self.client.force_authenticate(user=self.cuidador)

    def test_medicamento_cada_8_horas_genera_3_recordatorios(self):
        response = self.client.post('/api/medications/', {
            'patient': self.paciente.id,
            'nombre': 'Paracetamol',
            'dosis': '500mg',
            'frecuencia_horas': 8,
            'duracion_cantidad': 5,
            'duracion_unidad': 'dias',
            'hora_inicio': '08:00:00',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['frecuencia'], 'Cada 8 horas')
        self.assertEqual(
            response.data['fecha_fin'],
            (datetime.date.today() + datetime.timedelta(days=5)).isoformat()
        )

        recordatorios = Reminder.objects.filter(
            medication_id=response.data['id']
        ).order_by('hora')

        self.assertEqual(recordatorios.count(), 3)

        horas = [str(r.hora) for r in recordatorios]
        self.assertEqual(horas, ['00:00:00', '08:00:00', '16:00:00'])

    def test_medicamento_cada_24_horas_genera_1_recordatorio(self):
        response = self.client.post('/api/medications/', {
            'patient': self.paciente.id,
            'nombre': 'Losartán',
            'dosis': '50mg',
            'frecuencia_horas': 24,
            'duracion_cantidad': 1,
            'duracion_unidad': 'meses',
            'hora_inicio': '09:30:00',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recordatorios = Reminder.objects.filter(
            medication_id=response.data['id']
        )

        self.assertEqual(recordatorios.count(), 1)
        self.assertEqual(str(recordatorios.first().hora), '09:30:00')

    def test_fecha_fin_se_calcula_segun_duracion(self):
        response = self.client.post('/api/medications/', {
            'patient': self.paciente.id,
            'nombre': 'Ibuprofeno',
            'dosis': '400mg',
            'frecuencia_horas': 12,
            'duracion_cantidad': 10,
            'duracion_unidad': 'dias',
            'hora_inicio': '07:00:00',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recordatorio = Reminder.objects.filter(
            medication_id=response.data['id']
        ).first()

        fecha_esperada = datetime.date.today() + datetime.timedelta(days=10)

        self.assertEqual(recordatorio.fecha_fin, fecha_esperada)


# =====================================
# GENERACIÓN AUTOMÁTICA DE RECORDATORIOS DE CITAS
# =====================================

class GeneracionRecordatoriosCitaTests(APITestCase):
    """
    Verifica que al crear una cita médica con recordatorio=True se
    generen automáticamente 2 recordatorios: uno con anticipación
    y otro el mismo día de la cita.
    """

    def setUp(self):
        self.cuidador = User.objects.create_user(
            username='cuidador_citas',
            password='ContraseñaValida2024!',
        )

        self.paciente = Patient.objects.create(
            cuidador=self.cuidador,
            nombres='Ana', apellidos='Gómez',
            identificacion='555555', genero='femenino',
        )

        self.client.force_authenticate(user=self.cuidador)

    def test_cita_con_recordatorio_genera_dos_recordatorios(self):
        fecha_cita = datetime.date.today() + datetime.timedelta(days=10)

        response = self.client.post('/api/appointments/', {
            'patient': self.paciente.id,
            'fecha': fecha_cita.isoformat(),
            'hora': '10:00:00',
            'lugar': 'Clínica Central',
            'direccion': 'Calle 1',
            'barrio': 'Centro',
            'piso': '2',
            'consultorio': '204',
            'doctor': 'Dr. Pérez',
            'especialidad': 'Cardiología',
            'recordatorio': True,
            'recordatorio_antes_cantidad': 2,
            'recordatorio_antes_unidad': 'dias',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tipo'], 'consulta')

        recordatorios = Reminder.objects.filter(
            appointment_id=response.data['id']
        ).order_by('fecha')

        self.assertEqual(recordatorios.count(), 2)

        recordatorio_antes, recordatorio_dia = recordatorios

        self.assertEqual(
            recordatorio_antes.fecha,
            fecha_cita - datetime.timedelta(days=2)
        )
        self.assertEqual(recordatorio_dia.fecha, fecha_cita)

    def test_cita_sin_recordatorio_no_genera_ninguno(self):
        fecha_cita = datetime.date.today() + datetime.timedelta(days=10)

        response = self.client.post('/api/appointments/', {
            'patient': self.paciente.id,
            'fecha': fecha_cita.isoformat(),
            'hora': '10:00:00',
            'lugar': 'Clínica Central',
            'direccion': 'Calle 1',
            'barrio': 'Centro',
            'piso': '2',
            'consultorio': '204',
            'doctor': 'Dr. Pérez',
            'especialidad': 'Cardiología',
            'recordatorio': False,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recordatorios = Reminder.objects.filter(
            appointment_id=response.data['id']
        )

        self.assertEqual(recordatorios.count(), 0)


# =====================================
# PERFIL Y NOTIFICACIONES DE WHATSAPP
# =====================================

class PerfilWhatsAppTests(APITestCase):
    """
    Verifica que el cuidador pueda ver/guardar su configuración de
    WhatsApp, y que el mensaje de prueba use el helper de envío
    (simulado, sin llamar a CallMeBot de verdad).
    """

    def setUp(self):

        self.cuidador = User.objects.create_user(
            username='cuidador_whatsapp',
            password='ContraseñaValida2024!',
        )

        CaregiverProfile.objects.create(
            user=self.cuidador,
            identificacion='999999',
            genero='masculino',
        )

        self.client.force_authenticate(user=self.cuidador)

    def test_obtener_perfil(self):

        response = self.client.get('/api/perfil/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['whatsapp_numero'], '')

    def test_guardar_numero_y_apikey(self):

        response = self.client.patch('/api/perfil/', {
            'whatsapp_numero': '573001234567',
            'whatsapp_apikey': 'abc123',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.cuidador.caregiver_profile.refresh_from_db()

        self.assertEqual(
            self.cuidador.caregiver_profile.whatsapp_numero,
            '573001234567'
        )
        self.assertEqual(
            self.cuidador.caregiver_profile.whatsapp_apikey,
            'abc123'
        )

    @patch('medications.views.enviar_whatsapp')
    def test_probar_whatsapp_exitoso(self, mock_enviar):

        mock_enviar.return_value = 'ok'

        response = self.client.post('/api/perfil/probar-whatsapp/', {
            'whatsapp_numero': '573001234567',
            'whatsapp_apikey': 'abc123',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_enviar.assert_called_once()

    @patch('medications.views.enviar_whatsapp')
    def test_probar_whatsapp_sin_datos_falla(self, mock_enviar):

        from .whatsapp import WhatsAppError

        mock_enviar.side_effect = WhatsAppError('faltan datos')

        response = self.client.post('/api/perfil/probar-whatsapp/', {
            'whatsapp_numero': '',
            'whatsapp_apikey': '',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =====================================
# RECUPERAR CONTRASEÑA
# =====================================

class PasswordResetTests(APITestCase):
    """
    Verifica el flujo completo de recuperación de contraseña:
    pedir el enlace por correo, y usarlo para establecer una
    contraseña nueva.
    """

    def setUp(self):

        cache.clear()

        self.usuario = User.objects.create_user(
            username='usuario_reset',
            email='reset@test.com',
            password='ContraseñaValida2024!',
        )

    def _generar_uid_y_token(self, usuario):

        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)

        return uid, token

    def test_pedir_recuperacion_con_correo_existente_envia_correo(self):

        response = self.client.post('/api/password-reset/', {
            'email': 'reset@test.com',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('restablecer-password', mail.outbox[0].body)

    def test_pedir_recuperacion_con_correo_inexistente_no_falla(self):

        response = self.client.post('/api/password-reset/', {
            'email': 'no_existe@test.com',
        })

        # Misma respuesta genérica, sin revelar que el correo no existe.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_confirmar_con_token_valido_cambia_la_contrasena(self):

        uid, token = self._generar_uid_y_token(self.usuario)

        response = self.client.post('/api/password-reset-confirm/', {
            'uid': uid,
            'token': token,
            'password': 'NuevaContraseñaValida2024!',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.usuario.refresh_from_db()

        self.assertTrue(
            self.usuario.check_password('NuevaContraseñaValida2024!')
        )

    def test_confirmar_con_token_invalido_es_rechazado(self):

        uid, _ = self._generar_uid_y_token(self.usuario)

        response = self.client.post('/api/password-reset-confirm/', {
            'uid': uid,
            'token': 'token-invalido',
            'password': 'NuevaContraseñaValida2024!',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirmar_con_contrasena_debil_es_rechazado(self):

        uid, token = self._generar_uid_y_token(self.usuario)

        response = self.client.post('/api/password-reset-confirm/', {
            'uid': uid,
            'token': token,
            'password': '123',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

        self.usuario.refresh_from_db()

        # La contraseña original sigue intacta.
        self.assertTrue(
            self.usuario.check_password('ContraseñaValida2024!')
        )


# =====================================
# ACCESO SIN AUTENTICACIÓN
# =====================================

class AccesoSinAutenticacionTests(APITestCase):
    """
    Verifica que los endpoints protegidos rechacen peticiones
    sin token.
    """

    def test_listar_medicamentos_sin_token_es_rechazado(self):
        response = self.client.get('/api/medications/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_medicamento_sin_token_es_rechazado(self):
        response = self.client.post('/api/medications/', {
            'nombre': 'Aspirina',
            'dosis': '100mg',
            'frecuencia': 'diaria',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_pacientes_sin_token_es_rechazado(self):
        response = self.client.get('/api/patients/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
