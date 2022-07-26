from django.contrib import admin
from django.urls import reverse, path, register_converter
from subscriptions import models
from admin_auto_filters.filters import AutocompleteFilter
from import_export.admin import ImportExportModelAdmin
from ordered_model.admin import OrderedModelAdmin

from subscriptions.admin_views import (
    SubscriptionLetterTemplateEditorView,
    SubscriptionEmailTemplateEditorView,
    SubscriptionCategoryEmailTemplateEditorView,
    SubscriptionCategoryLetterTemplateEditorView,
    AdminEmailTemplateView,
    AdminLetterTemplateView,
)
from subscriptions.converters import (
    SubscriptionPkConverter,
    SubscriptionCategoryPkConverter,
    SubscriptionConverter,
    SubscriptionCategoryConverter,
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
    list_display = [
        "name",
        "category",
        "amount_used",
        "can_generate_letter",
        "can_generate_email",
        "get_has_registered_price",
    ]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        "can_generate_letter",
        "can_generate_email",
    ]

    def get_has_registered_price(self, obj):
        """Get if a subscription has a registered price."""
        return obj.has_registered_price()

    get_has_registered_price.boolean = True
    get_has_registered_price.short_description = "Has registered price"

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
        register_converter(SubscriptionPkConverter, "subscriptionpk")
        register_converter(SubscriptionConverter, "subscription")
        urls = super().get_urls()
        custom_urls = [
            path(
                "template-editor/<subscriptionpk:instance>/letter",
                SubscriptionLetterTemplateEditorView.as_view(),
                name="subscription_template_editor_letter",
            ),
            path(
                "template-editor/<subscriptionpk:instance>/email",
                SubscriptionEmailTemplateEditorView.as_view(),
                name="subscription_template_editor_email",
            ),
            path(
                "templates/<subscription:obj>/email",
                AdminEmailTemplateView.as_view(),
                name="subscription_email_template_download",
            ),
            path(
                "templates/<subscription:obj>/letter",
                AdminLetterTemplateView.as_view(),
                name="subscription_letter_template_download",
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

    title = "category"
    field_name = "category"


@admin.register(models.SubscriptionCategory)
class SubscriptionCategoryAdmin(ImportExportModelAdmin, OrderedModelAdmin):
    """Admin model for subscription categories."""

    search_fields = ["name"]
    list_display = ["name", "category", "move_up_down_links"]
    list_filter = [CategoryParentFilter, "category"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["category", "order"]

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
        register_converter(SubscriptionCategoryPkConverter, "categorypk")
        register_converter(SubscriptionCategoryConverter, "category")
        urls = super().get_urls()
        custom_urls = [
            path(
                "template-editor/<categorypk:instance>/letter",
                SubscriptionCategoryLetterTemplateEditorView.as_view(),
                name="subscription_category_template_editor_letter",
            ),
            path(
                "template-editor/<categorypk:instance>/email",
                SubscriptionCategoryEmailTemplateEditorView.as_view(),
                name="subscription_category_template_editor_email",
            ),
            path(
                "templates/<category:obj>/email",
                AdminEmailTemplateView.as_view(),
                name="subscription_category_email_template_download",
            ),
            path(
                "templates/<category:obj>/letter",
                AdminLetterTemplateView.as_view(),
                name="subscription_category_letter_template_download",
            ),
        ]
        return custom_urls + urls

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(models.SubscriptionSearchTerm)
class SubscriptionSearchTermAdmin(ImportExportModelAdmin):
    """Admin model for subscription search terms."""
