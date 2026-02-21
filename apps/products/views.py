from django_filters import rest_framework as filters
from rest_framework import generics

from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price"]


class ProductListView(generics.ListAPIView):
    """List products with filtering, search, and pagination."""

    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")
    serializer_class = ProductListSerializer
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "name"]


class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a single product by slug."""

    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
