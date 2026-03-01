"""Tests for the cart app — Session-based shopping cart."""
import pytest
from django.test import Client
from rest_framework.test import APIClient

from apps.products.models import Category, Product
from .models import Cart, CartItem


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def category(db):
    return Category.objects.create(name="Bebê", slug="bebe-cart")


@pytest.fixture
def product(db, category):
    from decimal import Decimal
    return Product.objects.create(
        name="Chupeta",
        slug="chupeta",
        description="Chupeta de silicone",
        price=Decimal("12.50"),
        stock=10,
        category=category,
        is_active=True,
    )


@pytest.fixture
def product_no_stock(db, category):
    return Product.objects.create(
        name="Produto Esgotado",
        slug="esgotado-cart",
        description="Sem estoque",
        price="5.00",
        stock=0,
        category=category,
        is_active=True,
    )


@pytest.fixture
def product_inactive(db, category):
    return Product.objects.create(
        name="Produto Inativo Cart",
        slug="inativo-cart",
        description="Inativo",
        price="8.00",
        stock=5,
        category=category,
        is_active=False,
    )


@pytest.fixture
def api_client():
    client = APIClient()
    # Ensure sessions are available
    from django.test import Client as DjangoClient
    return client


@pytest.fixture
def session_client(db):
    """Django test client with session support."""
    c = Client()
    c.get("/api/cart/")  # Initialize session
    return c


# ---------------------------------------------------------------------------
# Cart model tests
# ---------------------------------------------------------------------------

class TestCartModel:
    def test_str(self, db):
        cart = Cart.objects.create(session_key="abc12345678901234567890")
        assert "abc12345" in str(cart)

    def test_total_empty_cart(self, db):
        cart = Cart.objects.create(session_key="sess_total_empty")
        assert cart.total == 0

    def test_item_count_empty_cart(self, db):
        cart = Cart.objects.create(session_key="sess_count_empty")
        assert cart.item_count == 0

    def test_total_with_items(self, db, product):
        cart = Cart.objects.create(session_key="sess_total_items")
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        # 2 × 12.50 = 25.00
        assert cart.total == product.price * 2

    def test_item_count_with_items(self, db, product):
        cart = Cart.objects.create(session_key="sess_count_items")
        CartItem.objects.create(cart=cart, product=product, quantity=3)
        assert cart.item_count == 3


# ---------------------------------------------------------------------------
# CartItem model tests
# ---------------------------------------------------------------------------

class TestCartItemModel:
    def test_str(self, db, product):
        cart = Cart.objects.create(session_key="sess_cartitem_str")
        item = CartItem.objects.create(cart=cart, product=product, quantity=1)
        assert "Chupeta" in str(item)

    def test_subtotal(self, db, product):
        cart = Cart.objects.create(session_key="sess_subtotal")
        item = CartItem.objects.create(cart=cart, product=product, quantity=3)
        assert item.subtotal == product.price * 3

    def test_unique_together(self, db, product):
        """Cannot add same product twice to same cart."""
        from django.db import IntegrityError
        cart = Cart.objects.create(session_key="sess_unique")
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        with pytest.raises(IntegrityError):
            CartItem.objects.create(cart=cart, product=product, quantity=2)


# ---------------------------------------------------------------------------
# Cart API view tests
# ---------------------------------------------------------------------------

CART_URL = "/api/cart/"


class TestCartView:
    def test_get_empty_cart(self, client, db):
        response = client.get(CART_URL)
        assert response.status_code == 200
        assert response.data["item_count"] == 0

    def test_get_cart_fields(self, client, db):
        response = client.get(CART_URL)
        assert "items" in response.data
        assert "total" in response.data
        assert "item_count" in response.data

    def test_add_item_to_cart(self, client, product):
        response = client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 1},
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.data["item_count"] == 1

    def test_add_multiple_quantities(self, client, product):
        response = client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 3},
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.data["item_count"] == 3

    def test_add_same_product_accumulates(self, client, product):
        client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 2},
            content_type="application/json",
        )
        client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 3},
            content_type="application/json",
        )
        response = client.get(CART_URL)
        assert response.data["item_count"] == 5

    def test_add_nonexistent_product(self, client, db):
        response = client.post(
            CART_URL,
            {"product_id": 99999, "quantity": 1},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_add_inactive_product(self, client, product_inactive):
        response = client.post(
            CART_URL,
            {"product_id": product_inactive.id, "quantity": 1},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_add_exceeds_stock(self, client, product):
        response = client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 999},
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "Estoque" in response.data["error"]

    def test_add_product_no_stock(self, client, product_no_stock):
        response = client.post(
            CART_URL,
            {"product_id": product_no_stock.id, "quantity": 1},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_add_invalid_quantity_zero(self, client, product):
        """Quantity must be >= 1 (serializer validates min_value=1)."""
        response = client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 0},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_add_invalid_quantity_negative(self, client, product):
        response = client.post(
            CART_URL,
            {"product_id": product.id, "quantity": -5},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_add_missing_product_id(self, client, db):
        response = client.post(
            CART_URL,
            {"quantity": 1},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_cart_total_calculated(self, client, product):
        client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 2},
            content_type="application/json",
        )
        response = client.get(CART_URL)
        from decimal import Decimal
        assert Decimal(str(response.data["total"])) == product.price * 2

    def test_cart_persists_in_session(self, client, product):
        """Same client session should see persisted cart."""
        client.post(
            CART_URL,
            {"product_id": product.id, "quantity": 1},
            content_type="application/json",
        )
        response = client.get(CART_URL)
        assert response.data["item_count"] == 1


# ---------------------------------------------------------------------------
# get_or_create_cart helper tests
# ---------------------------------------------------------------------------

class TestGetOrCreateCart:
    def test_creates_cart_for_new_session(self, db):
        from apps.cart.views import get_or_create_cart

        class MockSession:
            session_key = None

            def create(self):
                self.session_key = "new_session_key_test"

        class MockRequest:
            session = MockSession()

        request = MockRequest()
        cart = get_or_create_cart(request)
        assert cart.session_key == "new_session_key_test"

    def test_returns_existing_cart(self, db):
        from apps.cart.views import get_or_create_cart

        Cart.objects.create(session_key="existing_sess_key_xyz")

        class MockRequest:
            class session:
                session_key = "existing_sess_key_xyz"

        cart = get_or_create_cart(MockRequest())
        assert cart.session_key == "existing_sess_key_xyz"
        assert Cart.objects.filter(session_key="existing_sess_key_xyz").count() == 1
