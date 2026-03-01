"""
Order signals — reduce stock when a new order is created.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, OrderItem

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrderItem)
def reduce_stock_on_order_item_save(sender, instance, created, **kwargs):
    """
    When an OrderItem is created, atomically reduce the product's stock.

    Uses F() expression to avoid race conditions in concurrent requests.
    """
    if not created:
        return  # Only on creation, not updates

    from django.db.models import F
    from apps.products.models import Product

    updated = Product.objects.filter(
        id=instance.product_id,
        stock__gte=instance.quantity,
    ).update(stock=F("stock") - instance.quantity)

    if updated:
        logger.info(
            "Stock reduced: product #%s — qty %s (order #%s)",
            instance.product_id,
            instance.quantity,
            instance.order_id,
        )
    else:
        logger.warning(
            "Could not reduce stock for product #%s (order #%s) — "
            "insufficient stock or product not found",
            instance.product_id,
            instance.order_id,
        )
