from rest_framework.generics import ListAPIView, RetrieveAPIView

from posts.api.v1.pagination import StandardResultsSetPagination
from posts.api.v1.serializers import PostSerializer
from posts.models import Post, STATUS_PUBLISHED


class PostListAPIView(ListAPIView):
    """
    Post List API View.

    Permissions required: None

    Use this endpoint to get a list of all Posts.
    """

    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=STATUS_PUBLISHED)
    pagination_class = StandardResultsSetPagination


class PostRetrieveAPIView(RetrieveAPIView):
    """
    Post Retrieve API View.

    Permissions required: None

    Use this endpoint to retrieve a Post.
    """

    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=STATUS_PUBLISHED)
