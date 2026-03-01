"""Pytest fixtures for BabyHappy e-commerce tests."""
import pytest


@pytest.fixture
def user(db):
    """Create a basic test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email='test@example.com',
        password='TestPassword123!',
        first_name='Test',
        last_name='User',
    )


@pytest.fixture
def admin_user(db):
    """Create a superuser for admin tests."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_superuser(
        email='admin@example.com',
        password='AdminPass123!',
        first_name='Admin',
        last_name='User',
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return a logged-in test client."""
    client.force_login(user)
    return client
