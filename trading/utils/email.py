from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_trade_email(user, transaction):
    """Envía un correo de confirmación de compra/venta."""
    action = 'Compra' if transaction.type == 'buy' else 'Venta'
    subject = f'CryptoNexus — {action} de {transaction.symbol} confirmada'

    # Intentar renderizar template HTML; fallback a texto plano
    try:
        html_message = render_to_string('emails/trade_confirmation.html', {
            'user': user,
            'transaction': transaction,
            'action': action,
        })
    except Exception:
        html_message = None

    plain_message = (
        f"Hola {user.username},\n\n"
        f"Tu {action.lower()} ha sido procesada exitosamente.\n\n"
        f"Detalles:\n"
        f"  Criptomoneda : {transaction.symbol}\n"
        f"  Cantidad     : {float(transaction.quantity):.6f}\n"
        f"  Precio       : ${float(transaction.price):,.2f} USD\n"
        f"  Total        : ${float(transaction.total):,.2f} USD\n"
        f"  Fecha        : {transaction.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        f"Nuevo balance disponible: ${float(user.balance):,.2f} USD\n\n"
        f"— El equipo de CryptoNexus"
    )

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as exc:
        logger.warning('No se pudo enviar el email de confirmación: %s', exc)


def send_welcome_email(user):
    """Envía un correo de bienvenida al registrar el usuario."""
    subject = 'CryptoNexus — Registro confirmado'

    plain_message = (
        f"Hola {user.username},\n\n"
        "Tu cuenta en CryptoNexus fue creada correctamente.\n"
        "Ya puedes iniciar sesión y empezar a operar con el balance demo.\n\n"
        "— El equipo de CryptoNexus"
    )

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as exc:
        logger.warning('No se pudo enviar el email de bienvenida: %s', exc)

