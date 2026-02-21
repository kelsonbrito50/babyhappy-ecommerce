from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "product_price", "quantity", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "name", "email", "cpf", "phone", "address",
            "status", "total", "items", "created_at",
        ]
        read_only_fields = ["status", "total", "items", "created_at"]


class CreateOrderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    cpf = serializers.CharField(max_length=14, required=False, default="")
    phone = serializers.CharField(max_length=20, required=False, default="")
    address = serializers.CharField()
