from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Subscription(models.Model):
    """Subscription model."""

    name = models.CharField(max_length=1024)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    support_email = models.EmailField(blank=True)
    support_reply_number = models.IntegerField(blank=True)
    support_postal_code = models.CharField(max_length=6, blank=True)
    support_city = models.CharField(max_length=1024, blank=True)
    correspondence_address = models.CharField(max_length=1024, blank=True)
    correspondence_postal_code = models.CharField(max_length=6, blank=True)
    correspondence_city = models.CharField(max_length=1024, blank=True)
    support_phone_number = PhoneNumberField(blank=True)
    cancellation_number = PhoneNumberField(blank=True)
    amount_used = models.PositiveIntegerField(default=1)
    category = models.ForeignKey('SubscriptionCategory', null=True, blank=True, on_delete=models.SET_NULL)


class SubscriptionCategory(models.Model):
    """Category for subscriptions."""

    name = models.CharField(max_length=1024)
    slug = models.SlugField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)

    class Meta:
        """
        Enforcing that there can not be two categories under a parent with same slug
        """

        unique_together = ('slug', 'parent')
        verbose_name = "Subscription category"
        verbose_name_plural = "Subscription categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent


class SubscriptionSearchTerm(models.Model):
    """Additional search terms for a Subscription"""

    name = models.CharField(max_length=1024)
    subscription = models.ManyToManyField('Subscription')
