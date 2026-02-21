from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from .gateway import cielo_gateway
from .models import Payment
from .serializers import AuthorizePaymentSerializer, CapturePaymentSerializer, PaymentSerializer


class CieloAuthorizeView(APIView):
    """Mock Cielo payment authorization endpoint."""

    def post(self, request):
        serializer = AuthorizePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]
        card_number = serializer.validated_data["card_number"]

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Pedido não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if hasattr(order, "payment"):
            return Response(
                {"error": "Pedido já possui pagamento"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = cielo_gateway.authorize(
            order_id=order.id,
            amount=float(order.total),
            card_number=card_number,
        )

        payment_status = Payment.Status.AUTHORIZED if result.success else Payment.Status.DENIED
        payment = Payment.objects.create(
            order=order,
            transaction_id=result.transaction_id,
            status=payment_status,
            amount=order.total,
            card_last_four=card_number[-4:],
            authorization_code=result.authorization_code,
        )

        if result.success:
            order.status = Order.Status.PAID
            order.save(update_fields=["status"])

        return Response(
            {
                "payment": PaymentSerializer(payment).data,
                "gateway_message": result.message,
            },
            status=status.HTTP_201_CREATED if result.success else status.HTTP_402_PAYMENT_REQUIRED,
        )


class CieloCaptureView(APIView):
    """Mock Cielo payment capture endpoint."""

    def post(self, request):
        serializer = CapturePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction_id = serializer.validated_data["transaction_id"]

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Transação não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if payment.status != Payment.Status.AUTHORIZED:
            return Response(
                {"error": "Transação não está autorizada para captura"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = cielo_gateway.capture(transaction_id)

        if result.success:
            payment.status = Payment.Status.CAPTURED
            payment.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "payment": PaymentSerializer(payment).data,
                "gateway_message": result.message,
            },
            status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST,
        )
