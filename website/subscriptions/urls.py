from django.urls import path
from .views import ListView, SummaryView, ListCategoryView, verification_send

urlpatterns = [
    path("", ListView.as_view(), name="overview",),
    path("<int:id>", ListCategoryView.as_view(), name="overview_category",),
    path("summary", SummaryView.as_view(), name="summary",),
    path("send", verification_send, name="send",),
]
