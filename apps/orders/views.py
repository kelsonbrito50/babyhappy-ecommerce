from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer


class OrderCreateView(APIView):
    """Create an order from the current cart."""

    def post(self, request):
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

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
