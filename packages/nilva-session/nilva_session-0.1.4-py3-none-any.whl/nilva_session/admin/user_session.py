from django.contrib import admin

from nilva_session.models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin page for UserSession model
    """

    list_display = (
        "id",
        "key",
        "user",
        "expire_at",
        "is_active",
        "detail",
        "last_online",
        "created_at",
    )
    readonly_fields = (
        "id",
        "user",
        "user_agent",
        "last_online",
        "last_ip",
        "expire_at",
        "key",
    )
    list_filter = ("is_active",)
