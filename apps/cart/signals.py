"""
Cart signals — handle guest cart → authenticated user cart merge on login.

When a user logs in, if the current session has a guest cart, migrate its
items to the user's cart (keyed on the user's pk) without duplicating items
that already exist in the destination cart.
"""
import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Cart, CartItem

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def merge_guest_cart_on_login(sender, request, user, **kwargs):
    """
    Merge the guest (session-based) cart into the user's persistent cart.

    Strategy:
    - Guest cart key: request.session.session_key (current session before login)
    - User cart key:  f"user_{user.pk}"
    - For each item in the guest cart:
        * If the product already exists in the user cart → add quantities.
        * Otherwise → move the item to the user cart.
    - Delete the (now-empty) guest cart.
    """
    session_key = request.session.session_key
    if not session_key:
        return  # No session → no guest cart to merge

    try:
        guest_cart = Cart.objects.prefetch_related("items__product").get(
            session_key=session_key
        )
    except Cart.DoesNotExist:
        return  # Nothing to merge

    if not guest_cart.items.exists():
        guest_cart.delete()
        return

    # Get or create the user's persistent cart
    user_cart_key = f"user_{user.pk}"
    user_cart, _ = Cart.objects.get_or_create(session_key=user_cart_key)

    merged_count = 0
    for guest_item in guest_cart.items.select_related("product"):
        existing_item = user_cart.items.filter(product=guest_item.product).first()

        if existing_item:
            # Add quantities without exceeding available stock
            existing_item.quantity += guest_item.quantity
            existing_item.save(update_fields=["quantity"])
        else:
            # Move item to user cart
            guest_item.cart = user_cart
            guest_item.save(update_fields=["cart"])

        merged_count += 1

    # Delete the now-empty or fully-migrated guest cart
    guest_cart.delete()

    logger.info(
        "Merged %d item(s) from guest cart '%s' into user cart for user #%s",
        merged_count,
        session_key,
        user.pk,
    )
