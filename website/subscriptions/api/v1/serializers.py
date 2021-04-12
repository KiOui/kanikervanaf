from subscriptions.models import Subscription, SubscriptionCategory
from rest_framework import serializers


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer."""

    class Meta:
        """Meta class."""

        model = Subscription
        fields = [
            "id",
            "name",
            "price",
            "support_email",
            "support_reply_number",
            "support_postal_code",
            "support_city",
            "correspondence_address",
            "correspondence_postal_code",
            "correspondence_city",
            "support_phone_number",
            "cancellation_number",
            "category",
        ]


class SubscriptionCategorySerializer(serializers.ModelSerializer):
    """Subscription category serializer."""

    class Meta:
        """Meta class."""

        model = SubscriptionCategory
        fields = ["id", "name", "parent"]
