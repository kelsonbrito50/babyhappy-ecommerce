"""
Custom admin configuration for the products app.

Features:
- ProductAdmin — rich list view, inline images, bulk actions
- CategoryAdmin — hierarchical category management
- Stock management actions
"""
from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from .models import Category, Product, ProductImage


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "order")
    ordering = ("order",)


# ---------------------------------------------------------------------------
# Category Admin
# ---------------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "product_count")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    def product_count(self, obj):
        count = obj.products.filter(is_active=True).count()
        return format_html('<span style="font-weight:bold">{}</span>', count)

    product_count.short_description = "Produtos ativos"


# ---------------------------------------------------------------------------
# Product Admin
# ---------------------------------------------------------------------------

@admin.action(description="Ativar produtos selecionados")
def activate_products(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} produto(s) ativado(s).")


@admin.action(description="Desativar produtos selecionados")
def deactivate_products(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} produto(s) desativado(s).")


@admin.action(description="Zerar estoque dos selecionados")
def zero_stock(modeladmin, request, queryset):
    updated = queryset.update(stock=0)
    modeladmin.message_user(request, f"Estoque zerado em {updated} produto(s).")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price_display",
        "stock_display",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = [ProductImageInline]
    actions = [activate_products, deactivate_products, zero_stock]

    fieldsets = (
        ("Informações básicas", {
            "fields": ("name", "slug", "category", "description"),
        }),
        ("Preço e estoque", {
            "fields": ("price", "stock"),
        }),
        ("Visibilidade", {
            "fields": ("is_active",),
        }),
        ("Auditoria", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def price_display(self, obj):
        return format_html("R$ {}", f"{obj.price:,.2f}")

    price_display.short_description = "Preço"
    price_display.admin_order_field = "price"

    def stock_display(self, obj):
        color = "red" if obj.stock == 0 else ("orange" if obj.stock < 5 else "green")
        return format_html(
            '<span style="color:{};font-weight:bold">{}</span>',
            color,
            obj.stock,
        )

    stock_display.short_description = "Estoque"
    stock_display.admin_order_field = "stock"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")
