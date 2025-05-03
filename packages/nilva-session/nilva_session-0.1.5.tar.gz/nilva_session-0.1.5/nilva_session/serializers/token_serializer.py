from typing import Any, Dict

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenBlacklistSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token, RefreshToken

from nilva_session.models import UserSession
from nilva_session.settings import DEFAULT


class TokenMixinBlacklistSerializer:

    @staticmethod
    def refresh_blacklist(refresh: RefreshToken, session_id=None):
        try:
            # Attempt to blacklist the given refresh token
            refresh.blacklist()
        except AttributeError:
            # If blacklist app not installed, `blacklist` method will
            # not be present
            pass

        if session_id:
            UserSession.objects.filter(id=session_id).update(is_active=False)


class TokenSessionObtainPairSerializer(TokenObtainPairSerializer):
    session_id_claim = getattr(settings, "USER_SESSION", {}).get(
        "SESSION_ID_CLAIM", DEFAULT["SESSION_ID_CLAIM"]
    )

    def get_token_by_session(cls, session: UserSession) -> Token:
        """
        Create and return a token for the given session.
        """
        token = super().get_token(session.user)
        token[cls.session_id_claim] = str(session.id)
        return token


class TokenSessionRefreshSerializer(
    TokenRefreshSerializer, TokenMixinBlacklistSerializer
):
    session_id_claim = getattr(settings, "USER_SESSION", {}).get(
        "SESSION_ID_CLAIM", DEFAULT["SESSION_ID_CLAIM"]
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])
        session_id = refresh.payload.get(self.session_id_claim, None)

        if session_id and (
            session := UserSession.objects.select_related("user").get(id=session_id)
        ):
            if not api_settings.USER_AUTHENTICATION_RULE(session.user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                self.refresh_blacklist(refresh, session_id)

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data


class TokenSessionBlacklistSerializer(
    TokenBlacklistSerializer, TokenMixinBlacklistSerializer
):
    session_id_claim = getattr(settings, "USER_SESSION", {}).get(
        "SESSION_ID_CLAIM", DEFAULT["SESSION_ID_CLAIM"]
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        refresh = self.token_class(attrs["refresh"])
        session_id = refresh.payload.get(self.session_id_claim)

        self.refresh_blacklist(refresh, session_id)

        return {}
