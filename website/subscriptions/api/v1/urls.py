from django.urls import path
from subscriptions.api.v1.views import (
    EmailRenderView,
    SubscriptionListAPIView,
    SubscriptionCategoryListAPIView,
    SubscriptionRetrieveAPIView,
    SubscriptionCategoryRetrieveAPIView,
)

urlpatterns = [
    path("", SubscriptionListAPIView.as_view(), name="subscription_list"),
    path(
        "<int:pk>", SubscriptionRetrieveAPIView.as_view(), name="subscription_retrieve"
    ),
    path(
        "categories",
        SubscriptionCategoryListAPIView.as_view(),
        name="subscription_category_list",
    ),
    path(
        "categories/<int:pk>",
        SubscriptionCategoryRetrieveAPIView.as_view(),
        name="subscription_category_retrieve",
    ),
    # path("render/<str:obj>/<str:slug>/email", EmailRenderView.as_view(), name="subscription_email_render"),
]
