"""
URL configuration for BabyHappy e-commerce.

Routes:
  /admin/              — Django admin
  /api/products/       — Legacy product list/detail endpoints
  /api/cart/           — Shopping cart endpoints
  /api/orders/         — Order creation endpoint
  /api/payments/       — Cielo payment endpoints

  /api/v1/             — DRF ViewSet router (v1 API)
    /api/v1/products/          — ProductViewSet (list, retrieve)
    /api/v1/categories/        — CategoryViewSet (list, retrieve)
    /api/v1/orders/            — OrderViewSet (list, retrieve, create)
    /api/v1/me/                — ProfileViewSet (me, update_me, change_password)

  /api/token/          — JWT obtain pair
  /api/token/refresh/  — JWT refresh

  /api/schema/         — OpenAPI 3.0 schema (YAML/JSON)
  /api/docs/           — Swagger UI interactive docs
  /api/redoc/          — ReDoc interactive docs
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.products.api import CategoryViewSet, ProductViewSet
from apps.orders.api import OrderViewSet
from apps.accounts.api import ProfileViewSet

# ---------------------------------------------------------------------------
# API v1 Router
# ---------------------------------------------------------------------------

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="v1-product")
router.register(r"categories", CategoryViewSet, basename="v1-category")
router.register(r"orders", OrderViewSet, basename="v1-order")
router.register(r"me", ProfileViewSet, basename="v1-profile")

# ---------------------------------------------------------------------------
# URL patterns
# ---------------------------------------------------------------------------

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Legacy endpoints (preserved for backwards compatibility)
    path("api/products/", include("apps.products.urls")),
    path("api/cart/", include("apps.cart.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/payments/", include("apps.payments.urls")),

    # API v1 — ViewSets
    path("api/v1/", include(router.urls)),

    # JWT authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # API documentation (drf-spectacular)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
