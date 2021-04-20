from django.urls.converters import SlugConverter, IntConverter
from .models import Subscription, SubscriptionCategory


class SubscriptionPkConverter(IntConverter):
    """Converter for Subscription model (for PKs)."""

    def to_python(self, value):
        """
        Cast int to Subscription.

        :param value: the integer to convert to a Subscription
        :type value: int
        :return: a Subscription or ValueError
        """
        try:
            return Subscription.objects.get(pk=int(value))
        except Subscription.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Subscription to a string.

        :param obj: the Subscription object
        :return: the public key of the Subscription object in string format
        """
        return str(obj.pk)


class SubscriptionCategoryPkConverter(IntConverter):
    """Converter for Subscription model (for PKs)."""

    def to_python(self, value):
        """
        Cast int to SubscriptionCategory.

        :param value: the integer to convert to a SubscriptionCategory
        :type value: int
        :return: a Subscription or ValueError
        """
        try:
            return SubscriptionCategory.objects.get(pk=int(value))
        except SubscriptionCategory.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of SubscriptionCategory to a string.

        :param obj: the SubscriptionCategory object
        :return: the public key of the SubscriptionCategory object in string format
        """
        return str(obj.pk)


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
        :return: the slug of the Subscription object in string format
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
