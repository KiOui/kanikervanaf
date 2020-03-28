from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

STATUS = ((0, "Draft"), (1, "Publish"))


class Post(models.Model):
    """Model for Post objects."""

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

    class Meta:
        """Meta class for Post objects."""

        ordering = ["-created_on"]
