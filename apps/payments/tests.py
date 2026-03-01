"""Tests for the payments app — Cielo mock gateway, payment status."""
import pytest
from rest_framework.test import APIClient

from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem
from .models import Payment
from .gateway import CieloGateway, CieloResponse


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def category(db):
    return Category.objects.create(name="Bebê Payments", slug="bebe-payments")


@pytest.fixture
def product(db, category):
    from decimal import Decimal
    return Product.objects.create(
        name="Carrinho de Bebê",
        slug="carrinho-bebe",
        description="Carrinho confortável",
        price=Decimal("350.00"),
        stock=5,
        category=category,
        is_active=True,
    )


@pytest.fixture
def order(db, product):
    from decimal import Decimal
    o = Order.objects.create(
        name="Pedro Alves",
        email="pedro@example.com",
        address="Rua Teste, 100",
        status=Order.Status.PENDING,
        total=Decimal("350.00"),
    )
    OrderItem.objects.create(
        order=o,
        product=product,
        product_name=product.name,
        product_price=product.price,
        quantity=1,
    )
    return o


@pytest.fixture
def authorized_payment(db, order):
    payment = Payment.objects.create(
        order=order,
        transaction_id="CIELO-DEMO-ABC123456789",
        status=Payment.Status.AUTHORIZED,
        amount=order.total,
        card_last_four="1234",
        authorization_code="AUTH-123456",
    )
    return payment


@pytest.fixture
def api_client():
    return APIClient()


AUTHORIZE_URL = "/api/payments/cielo/authorize/"
CAPTURE_URL = "/api/payments/cielo/capture/"


# ---------------------------------------------------------------------------
# Payment model tests
# ---------------------------------------------------------------------------

class TestPaymentModel:
    def test_str(self, authorized_payment):
        s = str(authorized_payment)
        assert "CIELO-DEMO-ABC123456789" in s
        assert "Autorizado" in s

    def test_status_choices(self):
        choices = [c[0] for c in Payment.Status.choices]
        assert "pending" in choices
        assert "authorized" in choices
        assert "captured" in choices
        assert "denied" in choices
        assert "refunded" in choices

    def test_one_to_one_order(self, authorized_payment, order):
        assert authorized_payment.order == order
        assert order.payment == authorized_payment

    def test_default_status_pending(self, db, order):
        p = Payment.objects.create(
            order=order,
            transaction_id="TX-DEFAULT-STATUS",
            amount=order.total,
            card_last_four="5678",
        )
        assert p.status == Payment.Status.PENDING


# ---------------------------------------------------------------------------
# Cielo Gateway unit tests
# ---------------------------------------------------------------------------

class TestCieloGateway:
    def setup_method(self):
        self.gateway = CieloGateway()

    def test_authorize_success(self):
        result = self.gateway.authorize(1, 100.0, "4111111111111111")
        assert result.success is True
        assert result.transaction_id.startswith("CIELO-DEMO-")
        assert result.authorization_code != ""

    def test_authorize_denied_with_0000_card(self):
        result = self.gateway.authorize(1, 100.0, "4111111111110000")
        assert result.success is False
        assert result.authorization_code == ""
        assert "negado" in result.message.lower()

    def test_authorize_returns_unique_transaction_ids(self):
        r1 = self.gateway.authorize(1, 100.0, "4111111111111111")
        r2 = self.gateway.authorize(1, 100.0, "4111111111111111")
        assert r1.transaction_id != r2.transaction_id

    def test_capture_success(self):
        auth = self.gateway.authorize(1, 100.0, "4111111111111111")
        result = self.gateway.capture(auth.transaction_id)
        assert result.success is True
        assert "capturado" in result.message.lower()

    def test_capture_invalid_transaction_id(self):
        result = self.gateway.capture("INVALID-TX-ID")
        assert result.success is False

    def test_capture_returns_cielo_response(self):
        auth = self.gateway.authorize(1, 50.0, "4111111111111111")
        result = self.gateway.capture(auth.transaction_id)
        assert isinstance(result, CieloResponse)


# ---------------------------------------------------------------------------
# Cielo Authorize View tests
# ---------------------------------------------------------------------------

class TestCieloAuthorizeView:
    def test_authorize_payment_success(self, api_client, order):
        response = api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": order.id,
                "card_number": "4111111111111111",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        assert response.status_code == 201
        assert "payment" in response.data

    def test_authorize_sets_order_paid(self, api_client, order):
        api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": order.id,
                "card_number": "4111111111111111",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        order.refresh_from_db()
        assert order.status == Order.Status.PAID

    def test_authorize_denied_card(self, api_client, order):
        response = api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": order.id,
                "card_number": "4111111111110000",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        assert response.status_code == 402

    def test_authorize_denied_payment_status(self, api_client, order):
        api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": order.id,
                "card_number": "4111111111110000",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        payment = Payment.objects.get(order=order)
        assert payment.status == Payment.Status.DENIED

    def test_authorize_nonexistent_order(self, api_client, db):
        response = api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": 99999,
                "card_number": "4111111111111111",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        assert response.status_code == 404

    def test_authorize_duplicate_payment_rejected(self, api_client, order, authorized_payment):
        response = api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": order.id,
                "card_number": "4111111111111111",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "já possui pagamento" in response.data["error"]

    def test_authorize_missing_card_number(self, api_client, order):
        response = api_client.post(
            AUTHORIZE_URL,
            {"order_id": order.id, "expiry": "12/2028", "cvv": "123"},
            format="json",
        )
        assert response.status_code == 400

    def test_authorize_stores_last_four_digits(self, api_client, order):
        response = api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": order.id,
                "card_number": "4111111111111234",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        assert response.data["payment"]["card_last_four"] == "1234"

    def test_authorize_gateway_message_returned(self, api_client, order):
        response = api_client.post(
            AUTHORIZE_URL,
            {
                "order_id": order.id,
                "card_number": "4111111111111111",
                "expiry": "12/2028",
                "cvv": "123",
            },
            format="json",
        )
        assert "gateway_message" in response.data


# ---------------------------------------------------------------------------
# Cielo Capture View tests
# ---------------------------------------------------------------------------

class TestCieloCaptureView:
    def test_capture_authorized_payment(self, api_client, authorized_payment):
        response = api_client.post(
            CAPTURE_URL,
            {"transaction_id": authorized_payment.transaction_id},
            format="json",
        )
        assert response.status_code == 200
        assert "payment" in response.data

    def test_capture_updates_status_to_captured(self, api_client, authorized_payment):
        api_client.post(
            CAPTURE_URL,
            {"transaction_id": authorized_payment.transaction_id},
            format="json",
        )
        authorized_payment.refresh_from_db()
        assert authorized_payment.status == Payment.Status.CAPTURED

    def test_capture_nonexistent_transaction(self, api_client, db):
        response = api_client.post(
            CAPTURE_URL,
            {"transaction_id": "TX-DOES-NOT-EXIST"},
            format="json",
        )
        assert response.status_code == 404

    def test_capture_already_captured_fails(self, api_client, authorized_payment):
        # First capture
        api_client.post(
            CAPTURE_URL,
            {"transaction_id": authorized_payment.transaction_id},
            format="json",
        )
        # Second capture attempt
        response = api_client.post(
            CAPTURE_URL,
            {"transaction_id": authorized_payment.transaction_id},
            format="json",
        )
        assert response.status_code == 400

    def test_capture_denied_payment_fails(self, api_client, db, order):
        denied_payment = Payment.objects.create(
            order=order,
            transaction_id="CIELO-DEMO-DENIED99",
            status=Payment.Status.DENIED,
            amount=order.total,
            card_last_four="0000",
        )
        response = api_client.post(
            CAPTURE_URL,
            {"transaction_id": denied_payment.transaction_id},
            format="json",
        )
        assert response.status_code == 400

    def test_capture_missing_transaction_id(self, api_client, db):
        response = api_client.post(
            CAPTURE_URL,
            {},
            format="json",
        )
        assert response.status_code == 400

    def test_capture_returns_gateway_message(self, api_client, authorized_payment):
        response = api_client.post(
            CAPTURE_URL,
            {"transaction_id": authorized_payment.transaction_id},
            format="json",
        )
        assert "gateway_message" in response.data
