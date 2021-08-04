from django.urls import path
from subscriptions.api.v1.views import (
    SubscriptionListAPIView,
    SubscriptionCategoryListAPIView,
    SubscriptionRetrieveAPIView,
    SubscriptionCategoryRetrieveAPIView,
    SubscriptionRenderLetterAPIView,
    SubscriptionRenderEmailAPIView,
    TemplateAPIView,
)


urlpatterns = [
    path("", SubscriptionListAPIView.as_view(), name="subscription_list"),
    path(
        "<int:pk>", SubscriptionRetrieveAPIView.as_view(), name="subscription_retrieve"
    ),
    path(
        "<int:pk>/render-letter",
        SubscriptionRenderLetterAPIView.as_view(),
        name="subscription_render_letter",
    ),
    path(
        "<int:pk>/render-email",
        SubscriptionRenderEmailAPIView.as_view(),
        name="subscription_render_email",
    ),
    path(
        "categories/<int:pk>",
        SubscriptionCategoryRetrieveAPIView.as_view(),
        name="subscription_category_retrieve",
    ),
    path(
        "render-template",
        TemplateAPIView.as_view(),
        name="render_template",
    ),
]
