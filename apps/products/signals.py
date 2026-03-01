"""
Product signals — invalidate cache when a product is saved or deleted.
"""
import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Product

logger = logging.getLogger(__name__)


def _invalidate_product_cache(product_id: int = None):
    """Clear cache keys related to product listings."""
    keys_to_delete = ["home_products", "product_list"]
    if product_id:
        keys_to_delete.append(f"product_detail_{product_id}")

    for key in keys_to_delete:
        cache.delete(key)
        logger.debug("Cache invalidated: %s", key)


@receiver(post_save, sender=Product)
def invalidate_product_cache_on_save(sender, instance, **kwargs):
    """Invalidate product-related cache when a product is created or updated."""
    _invalidate_product_cache(product_id=instance.id)
    logger.info("Product cache invalidated after save: #%s %s", instance.id, instance.name)


@receiver(post_delete, sender=Product)
def invalidate_product_cache_on_delete(sender, instance, **kwargs):
    """Invalidate product-related cache when a product is deleted."""
    _invalidate_product_cache(product_id=instance.id)
    logger.info(
        "Product cache invalidated after delete: #%s %s",
        instance.id,
        instance.name,
    )
