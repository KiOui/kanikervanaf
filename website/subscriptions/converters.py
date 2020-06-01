from django.urls.converters import IntConverter
from .models import Subscription


class SubscriptionConverter(IntConverter):
    """Converter for Subscription model."""

    def to_python(self, value):
        """
        Cast integer to Subscription.

        :param value: the public key of the Subscription
        :return: a Subscription or ValueError
        """
        try:
            return Subscription.objects.get(id=int(value))
        except Subscription.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Subscription to a string.

        :param obj: the Subscription object
        :return: the public key of the Subscription object in string format
        """
        return str(obj.pk)
