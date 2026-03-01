"""
Celery tasks for the payments app.

Tasks:
  send_payment_approved_task — notify the customer when payment is approved.
"""
import logging

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    name="payments.send_payment_approved",
)
def send_payment_approved_task(self, payment_id: int) -> None:
    """
    Send payment-approved e-mail to the customer.

    Args:
        payment_id: Primary key of the Payment instance.
    """
    from .models import Payment

    try:
        payment = Payment.objects.select_related("order").get(pk=payment_id)
    except Payment.DoesNotExist:
        logger.error("Payment #%s not found — skipping approval email", payment_id)
        return

    order = payment.order
    customer_email = order.email
    if not customer_email:
        logger.warning("Order #%s has no email — skipping payment approval email", order.pk)
        return

    PAYMENT_METHOD_LABELS = {
        "credit_card": "Cartão de crédito",
        "debit_card": "Cartão de débito",
        "pix": "PIX",
        "boleto": "Boleto bancário",
    }

    site_url = getattr(settings, "SITE_URL", "https://babyhappy.com.br")

    context = {
        "customer_name": order.name or "Cliente",
        "order_number": order.pk,
        "payment_method": PAYMENT_METHOD_LABELS.get("credit_card", "Cartão de crédito"),
        "payment_date": timezone.localtime(payment.updated_at).strftime("%d/%m/%Y %H:%M"),
        "transaction_id": payment.transaction_id,
        "amount": f"{payment.amount:.2f}",
        "site_url": site_url,
    }

    subject = f"Pagamento aprovado — Pedido #{order.pk} — BabyHappy"
    html_message = render_to_string("emails/payment_approved.html", context)
    plain_message = (
        f"Olá, {context['customer_name']}!\n\n"
        f"Seu pagamento de R$ {context['amount']} para o pedido #{order.pk} foi aprovado.\n"
        f"ID da transação: {payment.transaction_id}\n\n"
        "Acompanhe seu pedido no site."
    )

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        html_message=html_message,
        fail_silently=False,
    )

    logger.info(
        "Payment approved email sent to %s for payment #%s (order #%s)",
        customer_email,
        payment_id,
        order.pk,
    )
