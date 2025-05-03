from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from nilva_session.models import UserSession


class SessionSerializer(serializers.ModelSerializer):
    session_id = serializers.PrimaryKeyRelatedField(source="id", read_only=True)
    last_online = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserSession
        fields = (
            "session_id",
            "user_id",
            "user_agent_data",
            "last_online",
            "last_ip",
            "created_at",
        )

    def get_last_online(self, obj):
        request = self.context["request"]
        if isinstance(request.auth, AccessToken):
            return (
                obj.last_online
                if request.auth.get("session_id") != obj.id
                else timezone.now()
            )
        if isinstance(request.auth, UserSession):
            return obj.last_online if request.auth.id != obj.id else timezone.now()
        return obj.last_online
