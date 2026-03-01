"""
Celery tasks for the accounts app.

Tasks:
  send_verification_email_task — send account e-mail verification link.
"""
import logging

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    name="accounts.send_verification_email",
)
def send_verification_email_task(
    self,
    user_id: int,
    verification_url: str,
    expiry_hours: int = 24,
) -> None:
    """
    Send e-mail verification link to a newly registered user.

    Args:
        user_id:          Primary key of the CustomUser instance.
        verification_url: Full verification URL with signed token.
        expiry_hours:     Token validity period (shown in the email body).
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("User #%s not found — skipping verification email", user_id)
        return

    user_name = user.get_full_name() or user.email

    context = {
        "user_name": user_name,
        "verification_url": verification_url,
        "expiry_hours": expiry_hours,
    }

    subject = "Confirme seu e-mail — BabyHappy"
    html_message = render_to_string("emails/verification_email.html", context)
    plain_message = (
        f"Olá, {user_name}!\n\n"
        "Por favor confirme seu e-mail acessando o link abaixo:\n"
        f"{verification_url}\n\n"
        f"Este link expira em {expiry_hours} horas.\n\n"
        "Se você não criou uma conta, ignore este e-mail."
    )

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

    logger.info("Verification email sent to %s (user #%s)", user.email, user_id)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    name="accounts.send_welcome_email",
)
def send_welcome_email_task(self, user_id: int) -> None:
    """
    Send a welcome e-mail to a newly verified user.

    Args:
        user_id: Primary key of the CustomUser instance.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("User #%s not found — skipping welcome email", user_id)
        return

    user_name = user.get_full_name() or user.email
    site_url = getattr(settings, "SITE_URL", "https://babyhappy.com.br")

    context = {
        "user_name": user_name,
        "site_url": site_url,
    }

    subject = "Bem-vindo(a) ao BabyHappy! 🍼"
    html_message = render_to_string("emails/verification_email.html", context)
    plain_message = (
        f"Olá, {user_name}!\n\n"
        "Seja bem-vindo(a) ao BabyHappy!\n"
        "Sua conta foi verificada com sucesso.\n\n"
        f"Acesse nossa loja: {site_url}"
    )

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

    logger.info("Welcome email sent to %s (user #%s)", user.email, user_id)
