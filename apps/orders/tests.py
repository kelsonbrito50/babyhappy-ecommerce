"""Tests for the orders app — Order creation, status, items."""
import pytest
from django.test import Client
from rest_framework.test import APIClient

from apps.products.models import Category, Product
from apps.cart.models import Cart, CartItem
from .models import Order, OrderItem


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def category(db):
    return Category.objects.create(name="Bebê Orders", slug="bebe-orders")


@pytest.fixture
def product(db, category):
    from decimal import Decimal
    return Product.objects.create(
        name="Mamadeira",
        slug="mamadeira",
        description="Mamadeira anti-cólica",
        price=Decimal("35.90"),
        stock=20,
        category=category,
        is_active=True,
    )


@pytest.fixture
def product2(db, category):
    from decimal import Decimal
    return Product.objects.create(
        name="Biberon",
        slug="biberon",
        description="Biberon 250ml",
        price=Decimal("22.50"),
        stock=15,
        category=category,
        is_active=True,
    )


@pytest.fixture
def order_data():
    return {
        "name": "Maria Silva",
        "email": "maria@example.com",
        "cpf": "123.456.789-09",
        "phone": "(11) 99999-0000",
        "address": "Rua das Flores, 123 — São Paulo, SP",
    }


@pytest.fixture
def order(db, product):
    """Pre-created Order with one OrderItem."""
    from decimal import Decimal
    o = Order.objects.create(
        name="João Santos",
        email="joao@example.com",
        address="Av. Paulista, 1000",
        status=Order.Status.PENDING,
        total=Decimal("35.90"),
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
def client_with_cart(client, product, product2):
    """Test client with a session cart that has two items."""
    # Add items via POST to cart to ensure session is created
    client.post(
        "/api/cart/",
        {"product_id": product.id, "quantity": 2},
        content_type="application/json",
    )
    client.post(
        "/api/cart/",
        {"product_id": product2.id, "quantity": 1},
        content_type="application/json",
    )
    return client


# ---------------------------------------------------------------------------
# Order model tests
# ---------------------------------------------------------------------------

class TestOrderModel:
    def test_str(self, order):
        assert "João Santos" in str(order)
        assert f"#{order.id}" in str(order)

    def test_default_status_pending(self, db, product):
        o = Order.objects.create(
            name="Test", email="t@t.com", address="Rua 1"
        )
        assert o.status == Order.Status.PENDING

    def test_status_choices(self):
        choices = [c[0] for c in Order.Status.choices]
        assert "pending" in choices
        assert "paid" in choices
        assert "shipped" in choices
        assert "delivered" in choices
        assert "cancelled" in choices

    def test_calculate_total(self, order, product):
        order.calculate_total()
        assert order.total == product.price * 1

    def test_ordering_newest_first(self, db, product):
        o1 = Order.objects.create(name="A", email="a@a.com", address="Rua A")
        o2 = Order.objects.create(name="B", email="b@b.com", address="Rua B")
        orders = list(Order.objects.all())
        assert orders[0] == o2


# ---------------------------------------------------------------------------
# OrderItem model tests
# ---------------------------------------------------------------------------

class TestOrderItemModel:
    def test_str(self, order, product):
        item = order.items.first()
        assert "Mamadeira" in str(item)
        assert "1" in str(item)

    def test_subtotal(self, order, product):
        item = order.items.first()
        assert item.subtotal == product.price * 1

    def test_subtotal_multiple_qty(self, db, order, product):
        item = order.items.first()
        item.quantity = 3
        item.save()
        assert item.subtotal == product.price * 3


# ---------------------------------------------------------------------------
# Order Create View tests
# ---------------------------------------------------------------------------

ORDER_URL = "/api/orders/"


class TestOrderCreateView:
    def test_create_order_from_cart(self, client_with_cart, order_data):
        response = client_with_cart.post(
            ORDER_URL,
            order_data,
            content_type="application/json",
        )
        assert response.status_code == 201

    def test_create_order_has_correct_name(self, client_with_cart, order_data):
        response = client_with_cart.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        assert response.data["name"] == "Maria Silva"

    def test_create_order_has_items(self, client_with_cart, order_data):
        response = client_with_cart.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        assert len(response.data["items"]) == 2

    def test_create_order_calculates_total(self, client_with_cart, order_data, product, product2):
        response = client_with_cart.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        expected_total = (product.price * 2) + (product2.price * 1)
        from decimal import Decimal
        assert Decimal(str(response.data["total"])) == expected_total

    def test_create_order_clears_cart(self, client_with_cart, order_data):
        client_with_cart.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        response = client_with_cart.get("/api/cart/")
        assert response.data["item_count"] == 0

    def test_create_order_sets_pending_status(self, client_with_cart, order_data):
        response = client_with_cart.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        assert response.data["status"] == "pending"

    def test_create_order_empty_cart_fails(self, client, db, order_data):
        response = client.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        assert response.status_code == 400
        assert "Carrinho vazio" in response.data["error"]

    def test_create_order_no_session_fails(self, order_data):
        """Fresh client with no session = empty cart error."""
        c = Client()
        response = c.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        assert response.status_code == 400

    def test_create_order_missing_name(self, client_with_cart):
        response = client_with_cart.post(
            ORDER_URL,
            {"email": "test@test.com", "address": "Rua X"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_order_missing_email(self, client_with_cart):
        response = client_with_cart.post(
            ORDER_URL,
            {"name": "Test", "address": "Rua X"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_order_invalid_email(self, client_with_cart):
        response = client_with_cart.post(
            ORDER_URL,
            {"name": "Test", "email": "not-an-email", "address": "Rua X"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_order_missing_address(self, client_with_cart):
        response = client_with_cart.post(
            ORDER_URL,
            {"name": "Test", "email": "test@test.com"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_order_optional_cpf_phone(self, client_with_cart):
        """CPF and phone are optional."""
        response = client_with_cart.post(
            ORDER_URL,
            {
                "name": "Ana Lima",
                "email": "ana@example.com",
                "address": "Rua das Acácias, 42",
            },
            content_type="application/json",
        )
        assert response.status_code == 201

    def test_create_order_stores_product_snapshot(self, client_with_cart, order_data, product):
        """OrderItem stores a snapshot of price/name at time of order."""
        response = client_with_cart.post(
            ORDER_URL, order_data, content_type="application/json"
        )
        item = next(
            i for i in response.data["items"]
            if i["product_name"] == product.name
        )
        from decimal import Decimal
        assert Decimal(str(item["product_price"])) == product.price


# ---------------------------------------------------------------------------
# Order status transition tests
# ---------------------------------------------------------------------------

class TestOrderStatusTransitions:
    def test_transition_pending_to_paid(self, order):
        order.status = Order.Status.PAID
        order.save()
        order.refresh_from_db()
        assert order.status == "paid"

    def test_transition_paid_to_shipped(self, order):
        order.status = Order.Status.SHIPPED
        order.save()
        order.refresh_from_db()
        assert order.status == "shipped"

    def test_transition_shipped_to_delivered(self, order):
        order.status = Order.Status.DELIVERED
        order.save()
        order.refresh_from_db()
        assert order.status == "delivered"

    def test_transition_to_cancelled(self, order):
        order.status = Order.Status.CANCELLED
        order.save()
        order.refresh_from_db()
        assert order.status == "cancelled"

    def test_all_status_labels(self):
        assert Order.Status.PENDING.label == "Pendente"
        assert Order.Status.PAID.label == "Pago"
        assert Order.Status.SHIPPED.label == "Enviado"
        assert Order.Status.DELIVERED.label == "Entregue"
        assert Order.Status.CANCELLED.label == "Cancelado"
