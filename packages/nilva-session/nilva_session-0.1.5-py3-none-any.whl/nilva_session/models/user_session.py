import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from user_agents import parse
from user_agents.parsers import UserAgent

from nilva_session.settings import DEFAULT
from nilva_session.utils import token_generator, token_expire_at_generator


class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        verbose_name=_("user"),
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    key = models.CharField(
        verbose_name=_("key"), default=token_generator, max_length=64, unique=True
    )
    expire_at = models.DateTimeField(
        verbose_name=_("expire at"),
        default=token_expire_at_generator,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_("is active"), default=True)
    last_online = models.DateTimeField(verbose_name=_("last online"), auto_now=True)
    last_ip = models.GenericIPAddressField(
        verbose_name=_("last ip"), protocol="both", unpack_ipv4=True
    )
    user_agent = models.TextField(verbose_name=_("user agent"))
    detail = models.TextField(verbose_name=_("detail"), null=True, blank=True)
    created_at = models.DateTimeField(
        verbose_name=_("created at"), auto_now_add=True, editable=False
    )

    def __str__(self):
        return f"token {self.key}"

    class Meta:
        db_table = "user_session"
        verbose_name = _("user session")
        verbose_name_plural = _("user sessions")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.invalidate_cache(self.key)
            self.invalidate_cache_by_session_id(self.id)
        super().save(*args, **kwargs)

    @classmethod
    def get_cache_key(cls, key):
        prefix_cache_key = getattr(settings, "USER_SESSION", {}).get(
            "SESSION_CACHE_PREFIX", DEFAULT["SESSION_CACHE_PREFIX"]
        )
        return f"{prefix_cache_key}{key}"

    @classmethod
    def get_cache_key_by_session_id(cls, session_id):
        prefix_cache_key = getattr(settings, "USER_SESSION", {}).get(
            "SESSION_ID_CACHE_PREFIX", DEFAULT["SESSION_ID_CACHE_PREFIX"]
        )
        return f"{prefix_cache_key}{session_id}"

    @classmethod
    def invalidate_cache(cls, key):
        cache_key = cls.get_cache_key(key)
        cache.delete(cache_key)

    @classmethod
    def invalidate_cache_by_session_id(cls, session_id):
        cache_key = cls.get_cache_key_by_session_id(session_id)
        cache.delete(cache_key)

    @property
    def is_expired(self):
        """
        Helper property to check if the session is expired.
        """
        if self.expire_at and self.expire_at < timezone.now():
            self.save(update_fields=["last_online"])
            return True
        return False

    @property
    def user_agent_data(self) -> dict | None:
        try:
            user_agent: UserAgent = parse(self.user_agent)

            return {
                "os": user_agent.os.family,
                "device_brand": user_agent.device.brand,
                "device_model": user_agent.device.model,
                "device_family": user_agent.device.family,
                "browser": user_agent.browser.family,
                "is_mobile": user_agent.is_mobile,
                "is_tablet": user_agent.is_tablet,
            }
        except Exception:
            return
