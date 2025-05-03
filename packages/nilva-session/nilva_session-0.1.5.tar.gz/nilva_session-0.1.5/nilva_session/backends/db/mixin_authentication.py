from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions


class UserSessionMixinAuthentication:
    session_cache_ttl = ...

    def set_session_cache(self, session):
        pass

    @staticmethod
    def update_last_ip(session, request):
        last_ip = request.META.get("REMOTE_ADDR")
        changed = False
        if session.last_ip != last_ip:
            session.last_ip = last_ip
            changed = True
        return session, changed

    def check_user_agent(self, session, request):
        session, changed = self.update_last_ip(session, request)
        if session.user_agent != request.META.get("HTTP_USER_AGENT"):
            session.is_active = False
            session.detail = _("User suspended; because user agent changed!")
            session.save()
            raise exceptions.AuthenticationFailed(_("User session is suspended."))

        if changed:
            session.save()

        self.set_session_cache(session)
        return session
