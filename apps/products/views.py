"""
Product views — listing, detail, and full-text search.

Full-text search strategy:
  - PostgreSQL: uses SearchVector + SearchRank for relevance ordering.
  - SQLite (tests/CI): falls back to icontains filters.
"""
import logging

from django.db import connection
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import generics

from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer

logger = logging.getLogger(__name__)


def _is_postgresql() -> bool:
    """Return True when the active database backend is PostgreSQL."""
    return connection.vendor == "postgresql"


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price"]


class ProductListView(generics.ListAPIView):
    """
    List active products with filtering, search, ordering, and pagination.

    Query params:
      search      — full-text search (PostgreSQL: ranked; SQLite: icontains)
      category    — filter by category slug
      min_price   — minimum price (inclusive)
      max_price   — maximum price (inclusive)
      ordering    — price | -price | name | -name | created_at | -created_at
    """

    serializer_class = ProductListSerializer
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "name"]

    def get_queryset(self):
        base_qs = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images")
        )

        search_term = self.request.query_params.get("search", "").strip()

        if not search_term:
            return base_qs

        # ------------------------------------------------------------------
        # PostgreSQL: full-text search with SearchVector + SearchRank
        # ------------------------------------------------------------------
        if _is_postgresql():
            try:
                from django.contrib.postgres.search import (
                    SearchQuery,
                    SearchRank,
                    SearchVector,
                )

                vector = SearchVector("name", weight="A") + SearchVector(
                    "description", weight="B"
                )
                query = SearchQuery(search_term, config="portuguese")

                return (
                    base_qs.annotate(rank=SearchRank(vector, query))
                    .filter(rank__gte=0.01)
                    .order_by("-rank")
                )
            except Exception:  # pragma: no cover
                logger.exception(
                    "Full-text search failed for term '%s', falling back to icontains",
                    search_term,
                )

        # ------------------------------------------------------------------
        # SQLite (test environment) / fallback: simple icontains
        # ------------------------------------------------------------------
        return base_qs.filter(
            Q(name__icontains=search_term)
            | Q(description__icontains=search_term)
        )


class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a single product by slug."""

    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
    )
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
