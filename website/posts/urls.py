from django.urls import path
from .views import PostOverviewView, PostCreateView, PostDetailsView

urlpatterns = [
    path("overview", PostOverviewView.as_view(), name="post_overview"),
    path("create", PostCreateView.as_view(), name="post_create"),
    path("details/<int:id>", PostDetailsView.as_view(), name="details"),
]
