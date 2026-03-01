"""
DRF ViewSets for the products app.

Endpoints:
  GET  /api/v1/products/           — list with filters, search, pagination
  GET  /api/v1/products/{slug}/    — retrieve by slug
  GET  /api/v1/categories/         — list all categories
  GET  /api/v1/categories/{id}/    — retrieve category
"""
import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer
from .views import ProductFilter

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for product categories.

    list:   GET /api/v1/categories/
    retrieve: GET /api/v1/categories/{id}/
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    @extend_schema(
        summary="List all product categories",
        tags=["Categories"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a category",
        tags=["Categories"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for active products.

    list:     GET /api/v1/products/?category=bebe&min_price=10&search=fralda
    retrieve: GET /api/v1/products/{slug}/
    """

    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
    )
    permission_classes = [AllowAny]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "name"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    @extend_schema(
        summary="List active products",
        parameters=[
            OpenApiParameter("category", str, description="Filter by category slug"),
            OpenApiParameter("min_price", float, description="Minimum price"),
            OpenApiParameter("max_price", float, description="Maximum price"),
            OpenApiParameter("search", str, description="Search by name/description"),
            OpenApiParameter(
                "ordering",
                str,
                description="Order by: price, -price, created_at, name",
            ),
        ],
        tags=["Products"],
    )
    def list(self, request, *args, **kwargs):
        logger.debug("Product list requested — filters: %s", request.query_params)
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a product by slug",
        tags=["Products"],
    )
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        logger.debug("Product detail retrieved: %s", kwargs.get("slug"))
        return response
