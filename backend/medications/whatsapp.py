import urllib.request
import urllib.parse
import urllib.error


class WhatsAppError(Exception):
    """Se lanza cuando no se pudo enviar el mensaje de WhatsApp."""
    pass


def enviar_whatsapp(numero, apikey, mensaje):
    """
    Envía un mensaje de WhatsApp usando la API gratuita de CallMeBot
    (https://www.callmebot.com/blog/free-api-whatsapp-messages/).

    numero: número completo con código de país, sin '+' ni espacios
            (ej. '573001234567').
    apikey: la clave que CallMeBot entrega tras la activación.
    mensaje: texto a enviar.
    """

    if not numero or not apikey:

        raise WhatsAppError(
            'Falta el número de WhatsApp o la clave de API.'
        )

    texto = urllib.parse.quote(mensaje)

    url = (
        'https://api.callmebot.com/whatsapp.php'
        f'?phone={numero}&text={texto}&apikey={apikey}'
    )

    try:

        with urllib.request.urlopen(url, timeout=10) as response:

            return response.read().decode('utf-8', errors='ignore')

    except urllib.error.URLError as e:

        raise WhatsAppError(
            f'No se pudo conectar con CallMeBot: {e}'
        )

    except Exception as e:

        raise WhatsAppError(str(e))
