from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.settings import api_settings as jwt_settings


def _duration_breakdown(duration):
    total_seconds = int(duration.total_seconds())
    units = [
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]
    for unit_label, unit_seconds in units:
        if total_seconds % unit_seconds == 0 and total_seconds >= unit_seconds:
            amount = total_seconds // unit_seconds
            plural = "s" if amount != 1 else ""
            return total_seconds, f"{amount} {unit_label}{plural}"
    return total_seconds, f"{total_seconds} seconds"


class TokenResponseFormatter:
    access_output_field = "access_token"
    refresh_output_field = "refresh_token"

    def _format_response(self, data):
        formatted = {}
        if "access" in data:
            formatted[self.access_output_field] = data["access"]
            seconds, label = _duration_breakdown(
                jwt_settings.ACCESS_TOKEN_LIFETIME
            )
            formatted["access_token_expires_in"] = seconds
            formatted["access_token_expires_in_display"] = label
        if "refresh" in data:
            formatted[self.refresh_output_field] = data["refresh"]
            seconds, label = _duration_breakdown(
                jwt_settings.REFRESH_TOKEN_LIFETIME
            )
            formatted["refresh_token_expires_in"] = seconds
            formatted["refresh_token_expires_in_display"] = label
        # Preserve any other metadata returned by SimpleJWT (token_type, etc.)
        for key, value in data.items():
            if key in {"access", "refresh"}:
                continue
            formatted[key] = value
        return formatted


class CustomTokenObtainPairSerializer(TokenResponseFormatter, TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.setdefault("token_type", "Bearer")
        return self._format_response(data)


class CustomTokenRefreshSerializer(TokenResponseFormatter, TokenRefreshSerializer):
    refresh_token = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Alias for the `refresh` field.",
    )

    def validate(self, attrs):
        refresh_token = attrs.pop("refresh_token", None)
        if refresh_token and not attrs.get("refresh"):
            attrs["refresh"] = refresh_token
        data = super().validate(attrs)
        data.setdefault("token_type", "Bearer")
        return self._format_response(data)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
