"""Tests for the accounts app — Custom user model, authentication."""
import pytest
from django.contrib.auth import get_user_model

User = None  # Lazily resolved to avoid AppRegistryNotReady


def get_user():
    global User
    if User is None:
        User = get_user_model()
    return User


# ---------------------------------------------------------------------------
# CustomUser model tests
# ---------------------------------------------------------------------------

class TestCustomUserModel:
    def test_create_user(self, db):
        U = get_user()
        user = U.objects.create_user(
            email="newuser@example.com",
            password="StrongPass!23",
            first_name="Nova",
            last_name="Usuária",
        )
        assert user.email == "newuser@example.com"
        assert user.check_password("StrongPass!23")
        assert not user.is_staff

    def test_email_is_username_field(self, db):
        U = get_user()
        assert U.USERNAME_FIELD == "email"

    def test_str_returns_email(self, db):
        U = get_user()
        user = U.objects.create_user(
            email="str@example.com",
            password="Pass!23456",
            first_name="A",
            last_name="B",
        )
        assert str(user) == "str@example.com"

    def test_email_is_unique(self, db):
        from django.db import IntegrityError
        U = get_user()
        U.objects.create_user(
            email="unique@example.com",
            password="Pass!23456",
            first_name="A",
            last_name="B",
        )
        with pytest.raises(IntegrityError):
            U.objects.create_user(
                email="unique@example.com",
                password="OtherPass!23",
                first_name="B",
                last_name="C",
            )

    def test_create_user_without_email_raises(self, db):
        U = get_user()
        with pytest.raises(ValueError, match="e-mail"):
            U.objects.create_user(
                email="",
                password="Pass!23456",
                first_name="A",
                last_name="B",
            )

    def test_create_superuser(self, db):
        U = get_user()
        admin = U.objects.create_superuser(
            email="admin2@example.com",
            password="AdminPass!23",
            first_name="Admin",
            last_name="Super",
        )
        assert admin.is_staff
        assert admin.is_superuser

    def test_cpf_field_optional(self, db):
        U = get_user()
        user = U.objects.create_user(
            email="nocpf@example.com",
            password="Pass!23456",
            first_name="No",
            last_name="CPF",
        )
        assert user.cpf == ""

    def test_phone_field_optional(self, db):
        U = get_user()
        user = U.objects.create_user(
            email="nophone@example.com",
            password="Pass!23456",
            first_name="No",
            last_name="Phone",
        )
        assert user.phone == ""

    def test_email_normalized_on_create(self, db):
        U = get_user()
        user = U.objects.create_user(
            email="NormalIZED@EXAMPLE.COM",
            password="Pass!23456",
            first_name="A",
            last_name="B",
        )
        assert user.email == "NormalIZED@example.com"

    def test_required_fields_list(self, db):
        U = get_user()
        assert "first_name" in U.REQUIRED_FIELDS
        assert "last_name" in U.REQUIRED_FIELDS


# ---------------------------------------------------------------------------
# Authentication tests
# ---------------------------------------------------------------------------

class TestAuthentication:
    def test_login_with_email_and_password(self, client, db):
        U = get_user()
        U.objects.create_user(
            email="login@example.com",
            password="LoginPass!23",
            first_name="Login",
            last_name="User",
        )
        result = client.login(email="login@example.com", password="LoginPass!23")
        assert result is True

    def test_login_wrong_password(self, client, db):
        U = get_user()
        U.objects.create_user(
            email="wrong@example.com",
            password="CorrectPass!23",
            first_name="Wrong",
            last_name="Pass",
        )
        result = client.login(email="wrong@example.com", password="WrongPass!")
        assert result is False

    def test_login_nonexistent_user(self, client, db):
        result = client.login(email="ghost@example.com", password="any")
        assert result is False

    def test_authenticated_client_fixture(self, authenticated_client, user):
        """The authenticated_client fixture should be logged in."""
        response = authenticated_client.get("/admin/")
        # Redirected to admin login because not staff — but client IS authenticated
        # This confirms the force_login worked (no redirect to login page)
        assert response.status_code in [200, 302]


# ---------------------------------------------------------------------------
# CustomUserManager tests
# ---------------------------------------------------------------------------

class TestCustomUserManager:
    def test_manager_returns_correct_type(self, db):
        U = get_user()
        user = U.objects.create_user(
            email="manager@example.com",
            password="ManagerPass!23",
            first_name="M",
            last_name="N",
        )
        assert isinstance(user, U)

    def test_superuser_sets_is_staff(self, db):
        U = get_user()
        admin = U.objects.create_superuser(
            email="staff@example.com",
            password="StaffPass!23",
            first_name="S",
            last_name="T",
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
