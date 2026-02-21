from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "order", "transaction_id", "status", "amount",
            "card_last_four", "authorization_code", "created_at",
        ]


class AuthorizePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    card_number = serializers.CharField(max_length=19)
    expiry = serializers.CharField(max_length=7)
    cvv = serializers.CharField(max_length=4)


class CapturePaymentSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=100)
