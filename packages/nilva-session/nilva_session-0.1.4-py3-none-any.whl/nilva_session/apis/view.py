from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nilva_session.models import UserSession
from nilva_session.serializers import SessionSerializer


class ListDestroyActiveSessionsApi(generics.DestroyAPIView, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SessionSerializer
    queryset = UserSession.objects.filter(is_active=True).order_by("-last_online")

    @staticmethod
    def invalid_cache_sessions(queryset: list[UserSession]):
        for session_obj in queryset:
            UserSession.invalidate_cache(session_obj.key)
            UserSession.invalidate_cache_by_session_id(str(session_obj.id))

    def destroy(self, request, *args, **kwargs):
        token_ids = request.query_params.getlist("token_id")
        valid_token_ids = set(
            filter(lambda token_id: token_id != str(request.auth.id), token_ids)
        )

        queryset = self.get_queryset().filter(user=self.request.user)
        if valid_token_ids:
            queryset = queryset.filter(id__in=valid_token_ids)

        self.invalid_cache_sessions(queryset)

        deleted_count = queryset.update(is_active=False)

        return Response(
            {"detail": _("{} session(s) deleted.".format(deleted_count))},
            status=status.HTTP_204_NO_CONTENT,
        )
