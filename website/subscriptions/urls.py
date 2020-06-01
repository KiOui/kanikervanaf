from django.urls import path, register_converter
from .views import (
    SubscriptionDetailsSearchView,
    SubscriptionDetailsView,
    SubscriptionListView,
    SummaryView,
    ListCategoryView,
    ListCategoryPageView,
    RequestView,
    verification_send,
    search_database,
)
from .converters import SubscriptionConverter

register_converter(SubscriptionConverter, "subscription")

urlpatterns = [
    path("", SubscriptionListView.as_view(), name="overview",),
    path("<int:id>", ListCategoryView.as_view(), name="overview_category",),
    path(
        "<int:id>/page/<int:page>",
        ListCategoryPageView.as_view(),
        name="overview_category_page",
    ),
    path("summary", SummaryView.as_view(), name="summary",),
    path("send", verification_send, name="send",),
    path("search", search_database, name="search"),
    path("request", RequestView.as_view(), name="request"),
    path("details", SubscriptionDetailsSearchView.as_view(), name="details_search"),
    path(
        "details/<subscription:subscription>",
        SubscriptionDetailsView.as_view(),
        name="details",
    ),
]
