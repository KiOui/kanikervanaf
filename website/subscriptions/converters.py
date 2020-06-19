from django.urls.converters import SlugConverter
from .models import Subscription, SubscriptionCategory


class SubscriptionConverter(SlugConverter):
    """Converter for Subscription model."""

    def to_python(self, value):
        """
        Cast slug to Subscription.

        :param value: the slug of the Subscription
        :return: a Subscription or ValueError
        """
        try:
            return Subscription.objects.get(slug=value)
        except Subscription.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Subscription to a string.

        :param obj: the Subscription object
        :return: the public key of the Subscription object in string format
        """
        return str(obj.slug)


class SubscriptionCategoryConverter(SlugConverter):
    """Converter for SubscriptionCategory model."""

    def to_python(self, value):
        """
        Cast slug to SubscriptionCategory.

        :param value: the slug of the Subscription
        :return: a SubscriptionCategory or ValueError
        """
        try:
            return SubscriptionCategory.objects.get(slug=value)
        except SubscriptionCategory.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of SubscriptionCategory to a string.

        :param obj: the SubscriptionCategory object
        :return: the public key of the SubscriptionCategory object in string format
        """
        return str(obj.slug)
