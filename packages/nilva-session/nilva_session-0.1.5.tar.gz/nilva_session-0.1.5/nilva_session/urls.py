from django.urls import path

from nilva_session.apis import ListDestroyActiveSessionsApi

urlpatterns = [
    path(
        "active",
        ListDestroyActiveSessionsApi.as_view(),
        name="list-user-active-sessions",
    ),
]
