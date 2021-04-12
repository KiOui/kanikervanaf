from django.urls import path
from posts.api.v1.views import PostListAPIView, PostRetrieveAPIView

urlpatterns = [
    path("", PostListAPIView.as_view(), name="post_list"),
    path("<int:pk>", PostRetrieveAPIView.as_view(), name="post_retrieve"),
]
