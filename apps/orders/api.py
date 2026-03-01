"""
DRF ViewSets for the orders app.

Endpoints (session-owner only):
  GET  /api/v1/orders/       — list current session's orders
  GET  /api/v1/orders/{id}/  — retrieve a specific order
  POST /api/v1/orders/       — create order from cart (same as legacy endpoint)
"""
import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.cart.models import Cart
from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderSerializer

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.GenericViewSet):
    """
    ViewSet for orders — users can only see and create their own session's orders.

    Authentication is session-based (no login required; orders are tied to session_key).
    """

    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return only orders belonging to the current session."""
        session_key = self.request.session.session_key or ""
        return (
            Order.objects.filter(session_key=session_key)
            .prefetch_related("items")
            .order_by("-created_at")
        )

    @extend_schema(
        summary="List orders for the current session",
        tags=["Orders"],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Retrieve a specific order",
        tags=["Orders"],
    )
    def retrieve(self, request, pk=None, *args, **kwargs):
        session_key = request.session.session_key or ""
        try:
            order = Order.objects.get(id=pk, session_key=session_key)
        except Order.DoesNotExist:
            return Response(
                {"error": "Pedido não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @extend_schema(
        summary="Create an order from the current cart",
        request=CreateOrderSerializer,
        tags=["Orders"],
    )
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.session.session_key:
            return Response(
                {"error": "Carrinho vazio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart = Cart.objects.prefetch_related("items__product").get(
                session_key=request.session.session_key
            )
        except Cart.DoesNotExist:
            return Response(
                {"error": "Carrinho vazio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not cart.items.exists():
            return Response(
                {"error": "Carrinho vazio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            session_key=request.session.session_key,
            **serializer.validated_data,
        )

        for cart_item in cart.items.select_related("product"):
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
            )

        order.calculate_total()
        cart.items.all().delete()

        logger.info(
            "Order #%s created — session %s — total R$ %s",
            order.id,
            request.session.session_key[:8],
            order.total,
        )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
