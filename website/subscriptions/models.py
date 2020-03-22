from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import UserInformation
import secrets
import datetime


class Subscription(models.Model):
    """Subscription model."""

    name = models.CharField(max_length=1024)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    support_email = models.EmailField(blank=True)
    support_reply_number = models.CharField(max_length=10, blank=True)
    support_postal_code = models.CharField(max_length=6, blank=True)
    support_city = models.CharField(max_length=1024, blank=True)
    correspondence_address = models.CharField(max_length=1024, blank=True)
    correspondence_postal_code = models.CharField(max_length=6, blank=True)
    correspondence_city = models.CharField(max_length=1024, blank=True)
    support_phone_number = PhoneNumberField(blank=True)
    cancellation_number = PhoneNumberField(blank=True)
    amount_used = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(
        "SubscriptionCategory", null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        """
        Convert this object to string.

        :return: a string with the name of the subscription
        """
        return self.name

    @staticmethod
    def top_category(category, max_items=5, order_by="name"):
        """
        Get the top of a category.

        :param category: the category to search for the top items
        :param max_items: the maximum amount of items to put in the top
        :param order_by: the order by which to order the items
        :return: a list of Subscription objects being the top of a category
        """
        if max_items == 0:
            return Subscription.objects.filter(category=category).order_by(order_by)
        else:
            return Subscription.objects.filter(category=category).order_by(order_by)[
                :max_items
            ]

    def can_email(self):
        """
        Check if a subscription can be emailed to.

        :return: True if an email address is specified for the subscription object, False otherwise
        """
        return self.support_email is not None and self.support_email != ""

    def can_generate_pdf(self):
        """
        Check if a subscription can generate a PDF file.

        :return: True if there is enough information to generate a PDF file, False otherwise
        """
        return (
            self.support_reply_number is not None
            and self.support_postal_code is not None
            and self.support_reply_number != ""
            and self.support_postal_code != ""
        ) or (
            self.correspondence_address is not None
            and self.correspondence_postal_code is not None
            and self.correspondence_address != ""
            and self.correspondence_postal_code != ""
        )

    def deregistered(self):
        """
        Update the amount of times the subscription has been deregistered.

        Adds one to the amount of time this subscription has been used
        :return: None
        """
        self.amount_used += 1
        self.save()


class SubscriptionCategory(models.Model):
    """Category for subscriptions."""

    name = models.CharField(max_length=1024)
    slug = models.SlugField()
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )

    class Meta:
        """Enforcing that there can not be two categories under a parent with same slug."""

        unique_together = ("slug", "parent")
        verbose_name = "Subscription category"
        verbose_name_plural = "Subscription categories"

    def __str__(self):
        """
        Convert this object to a string.

        :return: a string with the name of the category
        """
        return self.name

    @staticmethod
    def get_top_level_categories():
        """
        Get all top level categories (categories without parents).

        :return: a set with all top level categories
        """
        return SubscriptionCategory.objects.filter(parent=None)


class SubscriptionSearchTerm(models.Model):
    """Additional search terms for a Subscription."""

    name = models.CharField(max_length=1024)
    subscription = models.ManyToManyField("Subscription")

    def __str__(self):
        """
        Convert this object to a string.

        :return: a string with the name of the search term
        """
        return self.name


class QueuedMailList(models.Model):
    """Submitted user list with subscriptions to deregister from."""

    token = models.CharField(max_length=64, null=False, blank=False, unique=True)
    item_list = models.ManyToManyField(Subscription)
    user_information = models.ForeignKey(
        UserInformation, blank=False, on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate(user_information, subscription_list):
        """
        Generate a new QueuedMailList by first creating a new random hexadecimal token of 32 bytes.

        :param user_information: the user information to add to the QueuedMailList
        :param subscription_list: the list with Subscription objects to add to the QueuedMailList
        :return: a QueuedMailList with a fresh token
        """
        random_token = secrets.token_hex(32)
        mail_list = QueuedMailList.objects.create(
            token=random_token, user_information=user_information
        )
        for item in subscription_list:
            mail_list.item_list.add(item)
        return mail_list

    def __str__(self):
        """
        Convert this object to a string.

        :return: a string with the token and the creation time
        """
        return "{}, created: {}".format(self.token, self.created)

    @staticmethod
    def remove_expired():
        """
        Remove all expired QueuedMailLists.

        :return: None
        """
        mail_lists = QueuedMailList.objects.all()
        remove_after = datetime.datetime.now() - datetime.timedelta(minutes=15)
        for mail_list in mail_lists:
            if mail_list.created <= remove_after:
                mail_list.user_information.delete()
                mail_list.delete()
