from django.db.models.signals import pre_save
from django.dispatch import receiver

from subscriptions.models import Subscription


@receiver(pre_save, sender=Subscription)
def set_can_generate_letter(sender, instance, **kwargs):
    """Set can_generate_letter when Subscription is saved."""
    instance.can_generate_letter = (
        bool(instance.support_reply_number)
        and bool(instance.support_postal_code)
        or bool(instance.correspondence_address)
        and bool(instance.correspondence_postal_code)
    )


@receiver(pre_save, sender=Subscription)
def set_can_generate_email(sender, instance, **kwargs):
    """Set can_generate_email when Subscription is saved."""
    instance.can_generate_email = bool(instance.support_email)
