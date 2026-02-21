from django.db import models

from apps.orders.models import Order


class Payment(models.Model):
    """Payment record with Cielo transaction tracking."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        AUTHORIZED = "authorized", "Autorizado"
        CAPTURED = "captured", "Capturado"
        DENIED = "denied", "Negado"
        REFUNDED = "refunded", "Estornado"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="pedido",
    )
    transaction_id = models.CharField("ID da transação", max_length=100, unique=True)
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    amount = models.DecimalField("valor", max_digits=10, decimal_places=2)
    card_last_four = models.CharField("últimos 4 dígitos", max_length=4)
    authorization_code = models.CharField("código de autorização", max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pagamento"
        verbose_name_plural = "pagamentos"

    def __str__(self):
        return f"Pagamento {self.transaction_id} — {self.get_status_display()}"
