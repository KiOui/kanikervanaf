from django.urls import path, register_converter
from .views import PostOverviewView, PostCreateView, PostDetailsView, PostUserOverview
from .converters import PostConverter

register_converter(PostConverter, "post")

urlpatterns = [
    path("overview/page/<int:page>", PostOverviewView.as_view(), name="post_overview"),
    path("create", PostCreateView.as_view(), name="post_create"),
    path("details/<post:post>/page/<int:page>", PostDetailsView.as_view(), name="details"),
    path("messages/page/<int:page>", PostUserOverview.as_view(), name="post_user_overview"),
]
