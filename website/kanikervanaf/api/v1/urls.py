from django.urls import path, include
from rest_framework.schemas import get_schema_view

from kanikervanaf.api.openapi import OpenAPISchemaGenerator

app_name = "kanikervanaf"

urlpatterns = [
    path("subscriptions/", include("subscriptions.api.v1.urls")),
    path("posts/", include("posts.api.v1.urls")),
    path(
        "schema",
        get_schema_view(
            title="API v1",
            url="/api/v1/",
            version=1,
            urlconf="kanikervanaf.api.v1.urls",
            generator_class=OpenAPISchemaGenerator,
        ),
        name="schema-v1",
    ),
]
