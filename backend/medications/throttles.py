from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Limita los intentos de login por IP, para dificultar ataques
    de fuerza bruta contra /api/token/.

    La tasa real (ej. '5/min') se define en settings.py, dentro de
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'].
    """

    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """
    Limita cuántas cuentas se pueden crear desde la misma IP en
    un periodo de tiempo, para evitar registro masivo automatizado.

    La tasa real se define en settings.py, dentro de
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['register'].
    """

    scope = 'register'


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Limita cuántas veces se puede pedir un correo de recuperación
    de contraseña desde la misma IP, para evitar spam de correos
    o intentos de enumerar cuentas existentes.

    La tasa real se define en settings.py, dentro de
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['password_reset'].
    """

    scope = 'password_reset'
