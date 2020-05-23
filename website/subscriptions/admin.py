from django.contrib import admin
from subscriptions import models
from admin_auto_filters.filters import AutocompleteFilter


class SubscriptionCategoryFilter(AutocompleteFilter):
    """Filter for subscription categories."""

    title = "category"
    field_name = "category"


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription categories are displayed inline."""

    search_fields = ["name"]
    list_filter = [SubscriptionCategoryFilter, "category"]
    list_display = ["name", "amount_used", "category"]

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
class SubscriptionCategoryAdmin(admin.ModelAdmin):
    """Admin model for subscription categories."""

    list_display = ["name", "parent"]
    list_filter = [CategoryParentFilter, "parent"]

    class Media:
        """Necessary to use AutocompleteFilter."""


admin.site.register(models.SubscriptionSearchTerm)
