from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import (

    RegisterView,

    PatientViewSet,
    PatientPDFView,

    MedicationViewSet,

    ReminderViewSet,

    MedicationHistoryViewSet,

    MedicalAppointmentViewSet,

    PerfilView,
    ProbarWhatsAppView,

    PasswordResetRequestView,
    PasswordResetConfirmView,

)

router = DefaultRouter()

router.register(
    r'patients',
    PatientViewSet,
    basename='patients'
)

router.register(
    r'medications',
    MedicationViewSet,
    basename='medications'
)

router.register(
    r'reminders',
    ReminderViewSet,
    basename='reminders'
)

router.register(
    r'history',
    MedicationHistoryViewSet,
    basename='history'
)

router.register(
    r'appointments',
    MedicalAppointmentViewSet,
    basename='appointments'
)

urlpatterns = [

    path(
        'register/',
        RegisterView.as_view(),
        name='register'
    ),

    path(
        'patients/<int:patient_id>/pdf/',
        PatientPDFView.as_view(),
        name='patient-pdf'
    ),

    path(
        'perfil/',
        PerfilView.as_view(),
        name='perfil'
    ),

    path(
        'perfil/probar-whatsapp/',
        ProbarWhatsAppView.as_view(),
        name='probar-whatsapp'
    ),

    path(
        'password-reset/',
        PasswordResetRequestView.as_view(),
        name='password-reset'
    ),

    path(
        'password-reset-confirm/',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm'
    ),

]

urlpatterns += router.urls