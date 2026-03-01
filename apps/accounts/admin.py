"""
Custom admin configuration for the accounts app.

Features:
- CustomUserAdmin — email-first authentication, CPF/phone fields, bulk actions
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser


@admin.action(description="Ativar usuários selecionados")
def activate_users(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} usuário(s) ativado(s).")


@admin.action(description="Desativar usuários selecionados")
def deactivate_users(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} usuário(s) desativado(s).")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "full_name",
        "cpf",
        "phone",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("email", "first_name", "last_name", "cpf")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"
    list_per_page = 25
    actions = [activate_users, deactivate_users]

    # Override UserAdmin fieldsets to remove `username`, add `cpf`/`phone`
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações pessoais", {
            "fields": ("first_name", "last_name", "cpf", "phone"),
        }),
        ("Permissões", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
            "classes": ("collapse",),
        }),
        ("Datas", {
            "fields": ("last_login", "date_joined"),
            "classes": ("collapse",),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "password1",
                "password2",
                "is_active",
                "is_staff",
            ),
        }),
    )

    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name or "—"

    full_name.short_description = "Nome completo"
    full_name.admin_order_field = "first_name"
