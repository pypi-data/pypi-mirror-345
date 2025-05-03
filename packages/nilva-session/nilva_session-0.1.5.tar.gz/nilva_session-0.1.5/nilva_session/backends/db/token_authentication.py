from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from nilva_session.backends.db.mixin_authentication import (
    UserSessionMixinAuthentication,
)
from nilva_session.models import UserSession
from nilva_session.settings import DEFAULT


class UserSessionDBTokenAuthentication(
    TokenAuthentication, UserSessionMixinAuthentication
):
    """
    Custom authentication that checks for user session validity, caching the session to avoid
    hitting the database repeatedly.
    """

    keyword = "Token"
    model = UserSession
    session_cache_ttl = getattr(settings, "USER_SESSION", {}).get(
        "SESSION_CACHE_TTL", DEFAULT["SESSION_CACHE_TTL"]
    )
    _request = None

    def authenticate(self, request):
        self._request = request
        return super(UserSessionDBTokenAuthentication, self).authenticate(request)

    def authenticate_credentials(self, key):
        """
        Authenticate the user session based on the provided token key.
        The session is cached, and token expiration and suspension are checked.
        """
        cache_key = self.model.get_cache_key(key)
        if session := cache.get(cache_key):
            session = self.check_user_agent(session, self._request)
            # Session found in cache, no need to query the database.
            return session.user, session

        try:
            # If not found in cache, retrieve session from the database.
            session = self.model.objects.select_related("user").get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        # Check if the session is suspended.
        if not session.is_active:
            raise exceptions.AuthenticationFailed(_("User session is suspended."))

        # Check if the session has expired.
        if session.is_expired:
            raise exceptions.AuthenticationFailed(
                _("Token has expired at {}").format(session.expire_at)
            )

        self.check_user_agent(session, self._request)
        return session.user, session

    @classmethod
    def create_user_session_from_request(cls, user, request, expire_at=None):
        last_ip = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")
        session = UserSession.objects.select_related("user").create(
            user=user, last_ip=last_ip, user_agent=user_agent, expire_at=expire_at
        )
        return session, session.key

    def set_session_cache(self, session):
        cache.set(
            UserSession.get_cache_key(session.key),
            session,
            timeout=self.session_cache_ttl,
        )
