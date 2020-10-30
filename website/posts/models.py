from django.db import models
from django.contrib.auth import get_user_model
from posts.services import send_post_status_update_email

User = get_user_model()

STATUS_DRAFT = 0
STATUS_PUBLISHED = 1

STATUS = ((STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Publish"))


class Post(models.Model):
    """Model for Post objects."""

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"

    title = models.CharField(max_length=256, blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
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
    status = models.IntegerField(choices=STATUS, default=0, help_text="If the status is updated, an email message will"
                                                                      "be send to the author of this post (if it is"
                                                                      "not anonymously placed).")

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
