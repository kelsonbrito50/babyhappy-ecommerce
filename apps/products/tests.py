"""Tests for the products app — Product listings, detail, filtering, search."""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Product, ProductImage


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def category(db):
    return Category.objects.create(name="Bebê", slug="bebe")


@pytest.fixture
def category2(db):
    return Category.objects.create(name="Brinquedos", slug="brinquedos")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Fraldas Premium",
        slug="fraldas-premium",
        description="Fralda macia para bebês",
        price="29.90",
        stock=50,
        category=category,
        is_active=True,
    )


@pytest.fixture
def product_no_stock(db, category):
    return Product.objects.create(
        name="Produto Esgotado",
        slug="produto-esgotado",
        description="Sem estoque",
        price="15.00",
        stock=0,
        category=category,
        is_active=True,
    )


@pytest.fixture
def product_inactive(db, category):
    return Product.objects.create(
        name="Produto Inativo",
        slug="produto-inativo",
        description="Não visível",
        price="10.00",
        stock=10,
        category=category,
        is_active=False,
    )


@pytest.fixture
def api_client():
    return APIClient()


# ---------------------------------------------------------------------------
# Category model tests
# ---------------------------------------------------------------------------

class TestCategoryModel:
    def test_str(self, category):
        assert str(category) == "Bebê"

    def test_slug_auto_generated(self, db):
        cat = Category(name="Nova Categoria")
        cat.save()
        assert cat.slug == "nova-categoria"

    def test_slug_not_overwritten(self, db):
        cat = Category(name="Nova", slug="my-custom-slug")
        cat.save()
        assert cat.slug == "my-custom-slug"

    def test_parent_category(self, db, category):
        child = Category.objects.create(name="Sub", slug="sub", parent=category)
        assert child.parent == category
        assert child in category.children.all()


# ---------------------------------------------------------------------------
# Product model tests
# ---------------------------------------------------------------------------

class TestProductModel:
    def test_str(self, product):
        assert str(product) == "Fraldas Premium"

    def test_in_stock_true(self, product):
        assert product.in_stock is True

    def test_in_stock_false(self, product_no_stock):
        assert product_no_stock.in_stock is False

    def test_slug_auto_generated(self, db, category):
        p = Product(
            name="Novo Produto",
            description="Desc",
            price="9.99",
            stock=5,
            category=category,
        )
        p.save()
        assert p.slug == "novo-produto"

    def test_ordering_newest_first(self, db, category):
        p1 = Product.objects.create(
            name="P1", slug="p1", description="d", price="1", stock=1, category=category
        )
        p2 = Product.objects.create(
            name="P2", slug="p2", description="d", price="2", stock=1, category=category
        )
        products = list(Product.objects.all())
        assert products[0] == p2  # newest first


# ---------------------------------------------------------------------------
# Product list view tests
# ---------------------------------------------------------------------------

class TestProductListView:
    url = "/api/products/"

    def test_list_active_products(self, api_client, product, product_inactive):
        response = api_client.get(self.url)
        assert response.status_code == 200
        ids = [p["id"] for p in response.data["results"]]
        assert product.id in ids
        assert product_inactive.id not in ids

    def test_empty_list(self, api_client, db):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_pagination_returns_count(self, api_client, product):
        response = api_client.get(self.url)
        assert "count" in response.data
        assert "results" in response.data

    def test_filter_by_category(self, api_client, product, category):
        response = api_client.get(self.url, {"category": category.slug})
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_filter_by_wrong_category(self, api_client, product):
        response = api_client.get(self.url, {"category": "nonexistent"})
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_filter_min_price(self, api_client, product):
        response = api_client.get(self.url, {"min_price": "50.00"})
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_filter_max_price(self, api_client, product):
        response = api_client.get(self.url, {"max_price": "100.00"})
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_filter_price_range(self, api_client, product):
        response = api_client.get(self.url, {"min_price": "10.00", "max_price": "50.00"})
        assert response.status_code == 200
        ids = [p["id"] for p in response.data["results"]]
        assert product.id in ids

    def test_search_by_name(self, api_client, product):
        response = api_client.get(self.url, {"search": "Fraldas"})
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_search_no_results(self, api_client, product):
        response = api_client.get(self.url, {"search": "xyz123nonexistent"})
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_ordering_by_price_asc(self, api_client, product, product_no_stock):
        response = api_client.get(self.url, {"ordering": "price"})
        assert response.status_code == 200

    def test_ordering_by_price_desc(self, api_client, product):
        response = api_client.get(self.url, {"ordering": "-price"})
        assert response.status_code == 200

    def test_product_fields(self, api_client, product):
        response = api_client.get(self.url)
        result = response.data["results"][0]
        assert "id" in result
        assert "name" in result
        assert "price" in result
        assert "stock" in result
        assert "in_stock" in result
        assert "category" in result

    def test_no_stock_product_included(self, api_client, product_no_stock):
        """Products with 0 stock are still listed (just in_stock=False)."""
        response = api_client.get(self.url)
        ids = [p["id"] for p in response.data["results"]]
        assert product_no_stock.id in ids
        result = next(p for p in response.data["results"] if p["id"] == product_no_stock.id)
        assert result["in_stock"] is False


# ---------------------------------------------------------------------------
# Product detail view tests
# ---------------------------------------------------------------------------

class TestProductDetailView:
    def get_url(self, slug):
        return f"/api/products/{slug}/"

    def test_get_product(self, api_client, product):
        response = api_client.get(self.get_url(product.slug))
        assert response.status_code == 200
        assert response.data["name"] == "Fraldas Premium"

    def test_product_detail_fields(self, api_client, product):
        response = api_client.get(self.get_url(product.slug))
        assert "description" in response.data
        assert "images" in response.data
        assert "category" in response.data

    def test_inactive_product_not_found(self, api_client, product_inactive):
        response = api_client.get(self.get_url(product_inactive.slug))
        assert response.status_code == 404

    def test_nonexistent_slug_404(self, api_client, db):
        response = api_client.get(self.get_url("does-not-exist"))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# ProductImage model tests
# ---------------------------------------------------------------------------

class TestProductImageModel:
    def test_str(self, db, product):
        img = ProductImage.objects.create(product=product, order=1)
        assert "Fraldas Premium" in str(img)
        assert "1" in str(img)
