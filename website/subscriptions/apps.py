from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    """Appconfig for subscriptions app."""

    name = "subscriptions"

    def ready(self):
        """
        Ready method.

        :return: None
        """
        from subscriptions import signals  # noqa
