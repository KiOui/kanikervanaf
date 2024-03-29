from django.urls import path, register_converter
from .views import (
    SubscriptionDetailsSearchView,
    SubscriptionDetailsView,
    SubscriptionDetailsRedirectView,
    SubscriptionListView,
    SummaryView,
    ListCategoryView,
    ListCategoryRedirectView,
    ListCategoryPageView,
    ListCategoryPageRedirectView,
    RequestView,
    verification_send,
    VerificationSendSucceeded,
    verify,
    VerificationSendFailed,
    AdminTemplateInformationView,
    BasicUserInformation,
)
from .converters import SubscriptionConverter, SubscriptionCategoryConverter

register_converter(SubscriptionConverter, "subscription")
register_converter(SubscriptionCategoryConverter, "category")

urlpatterns = [
    path(
        "",
        SubscriptionListView.as_view(),
        name="overview",
    ),
    path(
        "<category:category>",
        ListCategoryView.as_view(),
        name="overview_category",
    ),
    path(
        "<int:category>",
        ListCategoryRedirectView.as_view(),
        name="overview_category_redirect",
    ),
    path(
        "<category:category>/page/<int:page>",
        ListCategoryPageView.as_view(),
        name="overview_category_page",
    ),
    path(
        "<int:category>/page/<int:page>",
        ListCategoryPageRedirectView.as_view(),
        name="overview_category_page_redirect",
    ),
    path(
        "summary",
        SummaryView.as_view(),
        name="summary",
    ),
    path(
        "send",
        verification_send,
        name="send",
    ),
    path("request", RequestView.as_view(), name="request"),
    path("details", SubscriptionDetailsSearchView.as_view(), name="details_search"),
    path(
        "details/<subscription:subscription>",
        SubscriptionDetailsView.as_view(),
        name="details",
    ),
    path(
        "details/<int:subscription>",
        SubscriptionDetailsRedirectView.as_view(),
        name="details_redirect",
    ),
    path(
        "verify/<str:token>",
        verify,
        name="verify",
    ),
    path(
        "verification-request/succeeded",
        VerificationSendSucceeded.as_view(),
        name="verification_send_succeeded",
    ),
    path(
        "verification-request/failed",
        VerificationSendFailed.as_view(),
        name="verification_send_failed",
    ),
    path(
        "enter",
        BasicUserInformation.as_view(),
        name="enter",
    ),
    path(
        "admin/template-information",
        AdminTemplateInformationView.as_view(),
        name="admin_template_information",
    ),
]
