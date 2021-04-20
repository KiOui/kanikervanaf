from django.urls import path
from subscriptions.api.v1.views import (
    SubscriptionListAPIView,
    SubscriptionCategoryListAPIView,
    SubscriptionRetrieveAPIView,
    SubscriptionCategoryRetrieveAPIView,
    SubscriptionRenderLetterAPIView,
    SubscriptionRenderEmailAPIView,
    SubscriptionCategoryRenderLetterAPIView,
    SubscriptionCategoryRenderEmailAPIView,
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
        "categories",
        SubscriptionCategoryListAPIView.as_view(),
        name="subscription_category_list",
    ),
    path(
        "categories/<int:pk>/render-letter",
        SubscriptionCategoryRenderLetterAPIView.as_view(),
        name="subscription_category_render_letter",
    ),
    path(
        "categories/<int:pk>/render-email",
        SubscriptionCategoryRenderEmailAPIView.as_view(),
        name="subscription_category_render_email",
    ),
    path(
        "categories/<int:pk>",
        SubscriptionCategoryRetrieveAPIView.as_view(),
        name="subscription_category_retrieve",
    ),
    path("render-template", TemplateAPIView.as_view(), name="render_template",),
]
