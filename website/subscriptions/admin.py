from django.contrib import admin
from django.urls import reverse
from subscriptions import models
from admin_auto_filters.filters import AutocompleteFilter
from import_export.admin import ImportExportModelAdmin


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

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(models.SubscriptionSearchTerm)
class SubscriptionSearchTermAdmin(ImportExportModelAdmin):
    """Admin model for subscription search terms."""
