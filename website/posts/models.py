from django.db import models
from django.contrib.auth import get_user_model
from posts.services import send_post_status_update_email

User = get_user_model()

STATUS_DRAFT = 0
STATUS_PUBLISHED = 1

STATUS = ((STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published"))


class Post(models.Model):
    """Model for Post objects."""

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"

    title = models.CharField(max_length=256)
    author = models.ForeignKey(User, related_name="posts", on_delete=models.SET_NULL, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    response_to = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reactions",
    )
    status = models.IntegerField(
        choices=STATUS,
        default=0,
        help_text="If the status is updated, an email message will "
        "be send to the author of this post (if it is "
        "not anonymously placed).",
    )

    class Meta:
        """Meta class for Post objects."""

        ordering = ["-created_on"]

    def __str__(self):
        """
        Convert this object to string.

        :return: a string format of this object
        """
        return "{} - {}".format(self.title, self.post_date)

    def save(self, *args, **kwargs):
        """Save method."""
        if self.author is not None:
            try:
                current_instance = Post.objects.get(pk=self.pk)
                if current_instance.status != self.status:
                    send_post_status_update_email(self)
            except Post.DoesNotExist:
                pass
        super(Post, self).save(*args, **kwargs)

    @property
    def author_name(self):
        """
        Get the posts author.

        :return: the username of the author, Anoniem if the author is not set
        """
        return self.author.username

    @property
    def post_date(self):
        """
        Get the posts date of this object.

        :return: a formatted posts date of this object
        """
        return "{}".format(self.created_on.strftime(self.DATE_FORMAT))
