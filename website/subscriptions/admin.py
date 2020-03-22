from django.contrib import admin
from subscriptions import models


class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription categories are displayed inline."""

    search_fields = ["name"]


admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.SubscriptionCategory)
admin.site.register(models.SubscriptionSearchTerm)
admin.site.register(models.QueuedMailList)
