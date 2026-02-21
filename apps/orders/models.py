from django.db import models

from apps.products.models import Product


class Order(models.Model):
    """Customer order."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PAID = "paid", "Pago"
        SHIPPED = "shipped", "Enviado"
        DELIVERED = "delivered", "Entregue"
        CANCELLED = "cancelled", "Cancelado"

    name = models.CharField("nome completo", max_length=200)
    email = models.EmailField("e-mail")
    cpf = models.CharField("CPF", max_length=14, blank=True)
    phone = models.CharField("telefone", max_length=20, blank=True)
    address = models.TextField("endereço")
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total = models.DecimalField("total", max_digits=10, decimal_places=2, default=0)
    session_key = models.CharField("chave da sessão", max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pedido #{self.id} — {self.name}"

    def calculate_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=["total"])


class OrderItem(models.Model):
    """Individual item within an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="produto")
    product_name = models.CharField("nome do produto", max_length=300)
    product_price = models.DecimalField("preço unitário", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("quantidade")

    class Meta:
        verbose_name = "item do pedido"
        verbose_name_plural = "itens do pedido"

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def subtotal(self):
        return self.product_price * self.quantity
