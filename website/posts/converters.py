from django.urls.converters import IntConverter

from .models import Post


class PostConverter(IntConverter):
    """Converter for Post model."""

    def to_python(self, value):
        """
        Cast integer to Post.

        :param value: the public key of the Post
        :return: a Post or ValueError
        """
        try:
            return Post.objects.get(id=int(value))
        except Post.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Post to a string.

        :param obj: the Post object
        :return: the public key of the Post object in string format
        """
        return str(obj.pk)
