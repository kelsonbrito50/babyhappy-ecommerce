"""
DRF ViewSets for the accounts app.

Endpoints (authentication required):
  GET   /api/v1/me/         — retrieve current user profile
  PATCH /api/v1/me/         — update profile (name, phone, cpf)
  POST  /api/v1/me/change-password/  — change password
"""
import logging

from django.contrib.auth import get_user_model, update_session_auth_hash
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)
User = get_user_model()


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "cpf", "phone"]
        read_only_fields = ["id", "email"]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "As senhas não coincidem"}
            )
        return data


# ---------------------------------------------------------------------------
# ViewSet
# ---------------------------------------------------------------------------

class ProfileViewSet(viewsets.GenericViewSet):
    """
    ViewSet for the authenticated user's profile.

    me:              GET  /api/v1/me/
    update_me:       PATCH /api/v1/me/
    change_password: POST  /api/v1/me/change-password/
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Get current user profile",
        tags=["Profile"],
    )
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update current user profile",
        request=ProfileSerializer,
        tags=["Profile"],
    )
    @action(detail=False, methods=["patch"], url_path="me/update")
    def update_me(self, request):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Profile updated for user %s", request.user.email)
        return Response(serializer.data)

    @extend_schema(
        summary="Change account password",
        request=ChangePasswordSerializer,
        tags=["Profile"],
    )
    @action(detail=False, methods=["post"], url_path="me/change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["current_password"]):
            return Response(
                {"current_password": "Senha atual incorreta"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        update_session_auth_hash(request, user)
        logger.info("Password changed for user %s", user.email)
        return Response({"detail": "Senha alterada com sucesso"})
