from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Patient,
    CaregiverProfile,
    Medication,
    Reminder,
    MedicationHistory,
    MedicalAppointment
)

from .serializers import (
    RegisterSerializer,
    PatientSerializer,
    MedicationSerializer,
    ReminderSerializer,
    MedicationHistorySerializer,
    MedicalAppointmentSerializer,
    validar_password_fuerte,
)

from .throttles import (
    LoginRateThrottle,
    RegisterRateThrottle,
    PasswordResetRateThrottle,
)

from .pdf import generar_pdf_paciente
from .whatsapp import enviar_whatsapp, WhatsAppError


# =====================================
# LOGIN
# =====================================

class ThrottledTokenObtainPairView(TokenObtainPairView):
    """
    Igual al login estándar de simplejwt, pero con límite de
    intentos por IP para dificultar ataques de fuerza bruta.
    """

    throttle_classes = [LoginRateThrottle]


# =====================================
# REGISTRO
# =====================================

class RegisterView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =====================================
# RECUPERAR CONTRASEÑA
# =====================================

class PasswordResetRequestView(APIView):
    """
    Recibe un correo y, si pertenece a un usuario registrado, le
    envía un enlace para restablecer su contraseña. Por seguridad,
    la respuesta es siempre la misma sin importar si el correo
    existe o no (para no revelar qué cuentas están registradas).
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    MENSAJE_GENERICO = (
        'Si ese correo está registrado, te enviamos un enlace '
        'para restablecer tu contraseña.'
    )

    def post(self, request):

        email = request.data.get('email', '').strip()

        if email:

            usuario = User.objects.filter(email=email).first()

            if usuario:

                self._enviar_correo(usuario)

        return Response({
            'detail': self.MENSAJE_GENERICO
        })

    def _enviar_correo(self, usuario):

        uid = urlsafe_base64_encode(force_bytes(usuario.pk))

        token = default_token_generator.make_token(usuario)

        enlace = (
            f'{settings.FRONTEND_URL}/restablecer-password'
            f'?uid={uid}&token={token}'
        )

        send_mail(
            subject='Recupera tu contraseña de MedAlert',
            message=(
                f'Hola {usuario.first_name or usuario.username},\n\n'
                'Recibimos una solicitud para restablecer tu '
                'contraseña de MedAlert. Si fuiste tú, entra a este '
                f'enlace para elegir una nueva:\n\n{enlace}\n\n'
                'Si tú no pediste esto, puedes ignorar este correo.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            fail_silently=False,
        )


class PasswordResetConfirmView(APIView):
    """
    Recibe uid + token (los que llegaron por correo) y la nueva
    contraseña, valida todo, y si es correcto la actualiza.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):

        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        password = request.data.get('password', '')

        usuario = self._obtener_usuario(uid)

        if not usuario or not default_token_generator.check_token(usuario, token):

            return Response(
                {'detail': 'El enlace no es válido o ya expiró.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            validar_password_fuerte(password, usuario)

        except Exception as e:

            mensajes = getattr(e, 'detail', [str(e)])

            return Response(
                {'password': mensajes},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.set_password(password)
        usuario.save()

        return Response({
            'detail': 'Contraseña actualizada. Ya puedes iniciar sesión.'
        })

    def _obtener_usuario(self, uid):

        try:

            pk = force_str(urlsafe_base64_decode(uid))

            return User.objects.get(pk=pk)

        except Exception:

            return None


def _verificar_paciente_del_cuidador(serializer, request):
    """
    Evita que un cuidador cree/edite un registro (medicamento,
    recordatorio, cita, historial) apuntando al paciente de OTRO
    cuidador, aunque conozca su id.
    """

    patient = serializer.validated_data.get('patient')

    if patient is not None and patient.cuidador_id != request.user.id:

        raise PermissionDenied(
            'Ese paciente no pertenece a tu cuenta.'
        )


# =====================================
# PACIENTES
# =====================================

class PatientViewSet(viewsets.ModelViewSet):

    serializer_class = PatientSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]

    search_fields = ['nombres', 'apellidos', 'identificacion']

    def get_queryset(self):

        return Patient.objects.filter(
            cuidador=self.request.user
        ).order_by('nombres')

    def perform_create(self, serializer):

        serializer.save(
            cuidador=self.request.user
        )


class PatientPDFView(APIView):
    """
    Genera y devuelve el PDF de reporte de un paciente: sus datos,
    los del cuidador, medicamentos con su estado de tratamiento,
    historial de tomas y citas médicas agrupadas por tipo.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):

        try:

            patient = Patient.objects.get(id=patient_id)

        except Patient.DoesNotExist:

            raise NotFound('Paciente no encontrado.')

        if patient.cuidador_id != request.user.id:

            raise PermissionDenied(
                'Ese paciente no pertenece a tu cuenta.'
            )

        buffer = generar_pdf_paciente(patient, request.user)

        nombre_archivo = (
            f'reporte_{patient.nombres}_{patient.apellidos}.pdf'
        ).replace(' ', '_')

        response = HttpResponse(
            buffer,
            content_type='application/pdf'
        )

        response['Content-Disposition'] = (
            f'attachment; filename="{nombre_archivo}"'
        )

        return response


# =====================================
# PERFIL DEL CUIDADOR (WhatsApp)
# =====================================

class PerfilView(APIView):
    """
    Permite ver y actualizar los datos de notificación (WhatsApp)
    del cuidador autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        perfil, _ = CaregiverProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'identificacion': '',
                'genero': 'prefiero_no_decir',
            }
        )

        return Response({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'identificacion': perfil.identificacion,
            'genero': perfil.genero,
            'whatsapp_numero': perfil.whatsapp_numero,
            'whatsapp_apikey': perfil.whatsapp_apikey,
        })

    def patch(self, request):

        perfil, _ = CaregiverProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'identificacion': '',
                'genero': 'prefiero_no_decir',
            }
        )

        if 'whatsapp_numero' in request.data:

            perfil.whatsapp_numero = request.data['whatsapp_numero']

        if 'whatsapp_apikey' in request.data:

            perfil.whatsapp_apikey = request.data['whatsapp_apikey']

        perfil.save()

        return Response({
            'whatsapp_numero': perfil.whatsapp_numero,
            'whatsapp_apikey': perfil.whatsapp_apikey,
        })


class ProbarWhatsAppView(APIView):
    """
    Envía un mensaje de prueba para confirmar que la configuración
    de WhatsApp del cuidador funciona correctamente.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        numero = request.data.get('whatsapp_numero')
        apikey = request.data.get('whatsapp_apikey')

        if not numero or not apikey:

            perfil = getattr(request.user, 'caregiver_profile', None)

            if perfil:

                numero = numero or perfil.whatsapp_numero
                apikey = apikey or perfil.whatsapp_apikey

        try:

            enviar_whatsapp(
                numero,
                apikey,
                '✅ MedAlert: ¡tu WhatsApp quedó conectado correctamente!'
            )

            return Response({
                'detail': 'Mensaje de prueba enviado.'
            })

        except WhatsAppError as e:

            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# =====================================
# MEDICAMENTOS
# =====================================

class MedicationViewSet(viewsets.ModelViewSet):

    serializer_class = MedicationSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]

    search_fields = ['nombre', 'dosis']

    def get_queryset(self):

        queryset = Medication.objects.filter(
            patient__cuidador=self.request.user
        ).order_by('-created_at')

        patient_id = self.request.query_params.get('patient')

        if patient_id:

            queryset = queryset.filter(patient_id=patient_id)

        return queryset

    def perform_create(self, serializer):

        _verificar_paciente_del_cuidador(serializer, self.request)

        serializer.save()

    def perform_update(self, serializer):

        _verificar_paciente_del_cuidador(serializer, self.request)

        serializer.save()


# =====================================
# RECORDATORIOS
# =====================================

class ReminderViewSet(viewsets.ModelViewSet):

    serializer_class = ReminderSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]

    search_fields = ['medication__nombre', 'appointment__doctor']

    def get_queryset(self):

        queryset = Reminder.objects.filter(
            patient__cuidador=self.request.user
        ).order_by('hora')

        patient_id = self.request.query_params.get('patient')

        if patient_id:

            queryset = queryset.filter(patient_id=patient_id)

        return queryset

    def perform_create(self, serializer):

        _verificar_paciente_del_cuidador(serializer, self.request)

        serializer.save()

    def perform_update(self, serializer):

        _verificar_paciente_del_cuidador(serializer, self.request)

        serializer.save()


# =====================================
# HISTORIAL
# =====================================

class MedicationHistoryViewSet(viewsets.ModelViewSet):

    serializer_class = MedicationHistorySerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = MedicationHistory.objects.filter(
            patient__cuidador=self.request.user
        ).order_by('-tomado_en')

        patient_id = self.request.query_params.get('patient')

        if patient_id:

            queryset = queryset.filter(patient_id=patient_id)

        return queryset

    def perform_create(self, serializer):

        _verificar_paciente_del_cuidador(serializer, self.request)

        serializer.save()


# =====================================
# CITAS MÉDICAS
# =====================================

class MedicalAppointmentViewSet(viewsets.ModelViewSet):

    serializer_class = MedicalAppointmentSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]

    search_fields = ['doctor', 'especialidad', 'lugar']

    def get_queryset(self):

        queryset = MedicalAppointment.objects.filter(
            patient__cuidador=self.request.user
        ).order_by('fecha', 'hora')

        patient_id = self.request.query_params.get('patient')

        if patient_id:

            queryset = queryset.filter(patient_id=patient_id)

        tipo = self.request.query_params.get('tipo')

        if tipo:

            queryset = queryset.filter(tipo=tipo)

        return queryset

    def perform_create(self, serializer):

        _verificar_paciente_del_cuidador(serializer, self.request)

        serializer.save()

    def perform_update(self, serializer):

        _verificar_paciente_del_cuidador(serializer, self.request)

        serializer.save()
