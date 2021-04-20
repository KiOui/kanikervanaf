from django.contrib import admin, messages
from django.urls import reverse

from .models import Post, STATUS_DRAFT, STATUS_PUBLISHED


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin model for subscription categories."""

    list_display = ["title", "author", "response_to", "status"]
    list_filter = ["status"]

    actions = ["make_draft", "make_published"]

    def make_draft(self, request, queryset):
        """
        Make a QuerySet of posts draft.

        :param request: the request
        :param queryset: the queryset of posts
        :return: the request
        """
        messages.success(
            request,
            f"{queryset.filter(status=STATUS_PUBLISHED).update(status=STATUS_DRAFT)} posts were marked as draft",
        )
        return request

    make_draft.short_description = "Make selected posts drafts"

    def make_published(self, request, queryset):
        """
        Make a QuerySet of posts published.

        :param request: the request
        :param queryset: the queryset of posts
        :return: the request
        """
        messages.success(
            request,
            f"{queryset.filter(status=STATUS_DRAFT).update(status=STATUS_PUBLISHED)} posts were marked as published",
        )
        return request

    make_published.short_description = "Make selected posts published"

    def view_on_site(self, obj):
        """
        Get the URL for the frontend view of the post.

        :param obj: the post to get the frontend view for
        :return: the url to the post on the frontend
        """
        if obj.status == STATUS_PUBLISHED:
            return reverse("posts:details", kwargs={"post": obj, "page": 1})
        else:
            return None

    class Media:
        """Necessary to use AutocompleteFilter."""
