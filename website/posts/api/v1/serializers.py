from posts.models import Post
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    """Post serializer."""

    author = serializers.SerializerMethodField()

    def get_author(self, instance):
        """Get artist names instead of ID."""
        if instance.author is not None:
            return instance.author_name
        else:
            return None

    class Meta:
        """Meta class."""

        model = Post
        fields = [
            "title",
            "author",
            "updated_on",
            "created_on",
            "content",
            "response_to",
            "status",
        ]
