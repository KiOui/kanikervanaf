from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

STATUS = ((0, "Draft"), (1, "Publish"))


class Post(models.Model):
    """Model for Post objects."""

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"

    title = models.CharField(max_length=256, blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=False, null=False)
    response_to = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reactions",
    )
    status = models.IntegerField(choices=STATUS, default=0)

    @property
    def post_date(self):
        """
        Get the posts date of this object.

        :return: a formatted posts date of this object
        """
        return "{}".format(self.created_on.strftime(self.DATE_FORMAT))

    @property
    def get_author(self):
        """
        Get the posts author.

        :return: the username of the author, Anoniem if the author is not set
        """
        if self.author:
            return self.author.username
        else:
            return "Anoniem"

    def __str__(self):
        """
        Convert this object to string.

        :return: a string format of this object
        """
        return "{} - {}".format(self.title, self.post_date)

    class Meta:
        """Meta class for Post objects."""

        ordering = ["-created_on"]
