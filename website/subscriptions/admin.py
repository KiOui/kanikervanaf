from django.contrib import admin
from subscriptions import models


class SubscriptionCategoryInline(admin.StackedInline):
    """
    Display subscription categories as a stacked inline form in the admin panel.

    Show only subscription category objects that are explicitly created, do not show empty ones.
    """

    model = models.SubscriptionCategory
    extra = 0


class SubscriptionSearchTermInline(admin.StackedInline):
    """
    Display subscription search terms as a stacked inline form in the admin panel.

    Show only subscription search term objects that are explicitly created, do not show empty ones.
    """

    model = models.SubscriptionSearchTerm


class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription categories are displayed inline."""

    inlines = [
        SubscriptionCategoryInline,
        SubscriptionSearchTermInline,
    ]


admin.site.register(models.Subscription)
admin.site.register(models.SubscriptionCategory)
admin.site.register(models.SubscriptionSearchTerm)
