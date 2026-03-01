"""
Custom admin configuration for the orders app.

Features:
- OrderAdmin — inline items, status filters, date hierarchy, bulk actions
- OrderItemInline — read-only subtotal, product snapshot
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


# ---------------------------------------------------------------------------
# Inline
# ---------------------------------------------------------------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "product_price", "quantity", "subtotal")
    fields = ("product_name", "product_price", "quantity", "subtotal")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Bulk actions
# ---------------------------------------------------------------------------

@admin.action(description="Marcar como PAGO")
def mark_paid(modeladmin, request, queryset):
    updated = queryset.filter(status=Order.Status.PENDING).update(status=Order.Status.PAID)
    modeladmin.message_user(request, f"{updated} pedido(s) marcado(s) como Pago.")


@admin.action(description="Marcar como ENVIADO")
def mark_shipped(modeladmin, request, queryset):
    updated = queryset.filter(status=Order.Status.PAID).update(status=Order.Status.SHIPPED)
    modeladmin.message_user(request, f"{updated} pedido(s) marcado(s) como Enviado.")


@admin.action(description="Marcar como CANCELADO")
def mark_cancelled(modeladmin, request, queryset):
    updated = queryset.update(status=Order.Status.CANCELLED)
    modeladmin.message_user(request, f"{updated} pedido(s) marcado(s) como Cancelado.")


# ---------------------------------------------------------------------------
# Order Admin
# ---------------------------------------------------------------------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "status_badge",
        "total_display",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "cpf", "id")
    readonly_fields = ("created_at", "updated_at", "session_key")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    inlines = [OrderItemInline]
    actions = [mark_paid, mark_shipped, mark_cancelled]

    fieldsets = (
        ("Cliente", {
            "fields": ("name", "email", "cpf", "phone"),
        }),
        ("Entrega", {
            "fields": ("address",),
        }),
        ("Status e valor", {
            "fields": ("status", "total"),
        }),
        ("Metadados", {
            "fields": ("session_key", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    STATUS_COLORS = {
        "pending": "#f59e0b",    # amber
        "paid": "#10b981",       # emerald
        "shipped": "#3b82f6",    # blue
        "delivered": "#6366f1",  # indigo
        "cancelled": "#ef4444",  # red
    }

    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:bold">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def total_display(self, obj):
        return format_html("R$ {}", f"{obj.total:,.2f}")

    total_display.short_description = "Total"
    total_display.admin_order_field = "total"
