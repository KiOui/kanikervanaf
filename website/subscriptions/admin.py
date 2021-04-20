from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import reverse, path, register_converter
from subscriptions import models
from admin_auto_filters.filters import AutocompleteFilter
from import_export.admin import ImportExportModelAdmin

from subscriptions.admin_views import (
    SubscriptionLetterTemplateEditorView,
    SubscriptionEmailTemplateEditorView,
    SubscriptionCategoryEmailTemplateEditorView,
    SubscriptionCategoryLetterTemplateEditorView,
)
from subscriptions.converters import (
    SubscriptionPkConverter,
    SubscriptionCategoryPkConverter,
)


class SubscriptionCategoryFilter(AutocompleteFilter):
    """Filter for subscription categories."""

    title = "category"
    field_name = "category"


@admin.register(models.Subscription)
class SubscriptionAdmin(ImportExportModelAdmin):
    """Subscription categories are displayed inline."""

    search_fields = ["name"]
    list_filter = [SubscriptionCategoryFilter, "category"]
    list_display = ["name", "amount_used", "category"]
    prepopulated_fields = {"slug": ("name",)}

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Add a context to the extra_context.

        :param request: the request
        :param object_id: object id
        :param form_url: form url
        :param extra_context: extra content
        :return: changeform_view with added context
        """
        try:
            obj = models.Subscription.objects.get(id=object_id)
        except models.Subscription.DoesNotExist:
            obj = None
        try:
            extra_context["show_edit_letter"] = obj is not None
            extra_context["show_edit_email"] = obj is not None
            extra_context["format"] = "subscription"
        except TypeError:
            extra_context = {
                "show_edit_letter": obj is not None,
                "show_edit_email": obj is not None,
                "format": "subscription",
            }
        return self.changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        """Get admin urls."""
        register_converter(SubscriptionPkConverter, "subscription")
        urls = super().get_urls()
        custom_urls = [
            path(
                "template-editor/<subscription:instance>/letter",
                SubscriptionLetterTemplateEditorView.as_view(),
                name="subscription_template_editor_letter",
            ),
            path(
                "template-editor/<subscription:instance>/email",
                SubscriptionEmailTemplateEditorView.as_view(),
                name="subscription_template_editor_email",
            ),
        ]
        return custom_urls + urls

    def view_on_site(self, obj):
        """
        Get the URL for the frontend view of the subscription.

        :param obj: the subscription to get the frontend view for
        :return: the url to the subscription on the frontend
        """
        return reverse("subscriptions:details", kwargs={"subscription": obj})

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(models.QueuedMailList)
class QueuedMailListAdmin(admin.ModelAdmin):
    """Admin model for queued mail lists."""

    readonly_fields = ["created"]


class CategoryParentFilter(AutocompleteFilter):
    """Filter for subscription categories parents."""

    title = "parent"
    field_name = "parent"


@admin.register(models.SubscriptionCategory)
class SubscriptionCategoryAdmin(ImportExportModelAdmin):
    """Admin model for subscription categories."""

    list_display = ["name", "parent"]
    list_filter = [CategoryParentFilter, "parent"]
    prepopulated_fields = {"slug": ("name",)}

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Add a context to the extra_context.

        :param request: the request
        :param object_id: object id
        :param form_url: form url
        :param extra_context: extra content
        :return: changeform_view with added context
        """
        try:
            obj = models.Subscription.objects.get(id=object_id)
        except models.Subscription.DoesNotExist:
            obj = None
        try:
            extra_context["show_edit_letter"] = obj is not None
            extra_context["show_edit_email"] = obj is not None
            extra_context["format"] = "subscription-category"
        except TypeError:
            extra_context = {
                "show_edit_letter": obj is not None,
                "show_edit_email": obj is not None,
                "format": "subscription-category",
            }
        return self.changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        """Get admin urls."""
        register_converter(SubscriptionCategoryPkConverter, "category")
        urls = super().get_urls()
        custom_urls = [
            path(
                "template-editor/<category:instance>/letter",
                SubscriptionCategoryLetterTemplateEditorView.as_view(),
                name="subscription_category_template_editor_letter",
            ),
            path(
                "template-editor/<category:instance>/email",
                SubscriptionCategoryEmailTemplateEditorView.as_view(),
                name="subscription_category_template_editor_email",
            ),
        ]
        return custom_urls + urls

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(models.SubscriptionSearchTerm)
class SubscriptionSearchTermAdmin(ImportExportModelAdmin):
    """Admin model for subscription search terms."""
