"""
Celery tasks for the orders app.

Tasks:
  send_order_confirmation_task — e-mail the customer after order creation.
"""
import logging
from decimal import Decimal

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
    name="orders.send_order_confirmation",
)
def send_order_confirmation_task(self, order_id: int) -> None:
    """
    Send order confirmation e-mail to the customer.

    Args:
        order_id: Primary key of the Order instance.
    """
    from .models import Order

    try:
        order = Order.objects.prefetch_related("items").get(pk=order_id)
    except Order.DoesNotExist:
        logger.error("Order #%s not found — skipping confirmation email", order_id)
        return

    customer_email = order.email
    if not customer_email:
        logger.warning("Order #%s has no email — skipping confirmation email", order_id)
        return

    # Build context
    items_data = []
    for item in order.items.all():
        subtotal = Decimal(str(item.product_price)) * item.quantity
        items_data.append(
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "product_price": f"{item.product_price:.2f}",
                "subtotal": f"{subtotal:.2f}",
            }
        )

    site_url = getattr(settings, "SITE_URL", "https://babyhappy.com.br")

    context = {
        "customer_name": order.name or "Cliente",
        "order_number": order.pk,
        "order_date": timezone.localtime(order.created_at).strftime("%d/%m/%Y %H:%M"),
        "order_status": order.get_status_display(),
        "order_items": items_data,
        "order_total": f"{order.total:.2f}",
        "site_url": site_url,
    }

    subject = f"Pedido #{order.pk} confirmado — BabyHappy"
    html_message = render_to_string("emails/order_confirmation.html", context)
    plain_message = (
        f"Olá, {context['customer_name']}!\n\n"
        f"Seu pedido #{order.pk} foi confirmado.\n"
        f"Total: R$ {context['order_total']}\n\n"
        "Acesse o site para mais detalhes."
    )

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        html_message=html_message,
        fail_silently=False,
    )

    logger.info("Order confirmation email sent to %s for order #%s", customer_email, order_id)
