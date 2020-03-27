from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import UserInformation
import secrets
import datetime
import pytz
from django.conf import settings


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
    def top_category(category, max_items=5, order_by=None):
        """
        Get the top of a category.

        :param category: the category to search for the top items
        :param max_items: the maximum amount of items to put in the top
        :param order_by: the order by which to order the items
        :return: a list of Subscription objects being the top of a category
        """
        queryset = Subscription.objects.filter(category__in=category.get_family_tree())
        if order_by is not None:
            queryset = queryset.order_by(order_by)

        if max_items != 0:
            return queryset[:max_items]
        else:
            return queryset

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

    def get_address_information(self):
        """
        Get the address information of a subscription.

        First uses the support address (if complete), then uses the correspondence address
        :return: a tuple (address, postal_code, residence)
        """
        if (
            self.support_reply_number is not None
            and self.support_postal_code is not None
            and self.support_reply_number != ""
            and self.support_postal_code != ""
        ):
            return (
                self.support_reply_number,
                self.support_postal_code,
                self.support_city,
            )
        else:
            return (
                self.correspondence_address,
                self.correspondence_postal_code,
                self.correspondence_city,
            )

    def deregistered(self):
        """
        Update the amount of times the subscription has been deregistered.

        Adds one to the amount of time this subscription has been used
        :return: None
        """
        self.amount_used += 1
        self.save()

    def to_json(self):
        """
        Convert this object to a JSON compatible dictionary.

        :return: a dictionary containing the name, id, price, ability to email and ability to generate a PDF.
        """
        return {
            "name": self.name,
            "id": self.id,
            "price": float(self.price),
            "can_email": self.can_email(),
            "can_letter": self.can_generate_pdf(),
        }


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

    def get_children(self):
        """
        Get all the children of a category.

        :return: a QuerySet with all children of the category
        """
        return SubscriptionCategory.objects.filter(parent=self)

    def get_family_tree(self, already_visited=None):
        """
        Get all family members of a category.

        :param already_visited: against infinite recursion
        :return: a list with all family members of a category.
        """
        if already_visited is None:
            already_visited = [self]
        elif self in already_visited:
            return []
        else:
            already_visited.append(self)

        children = [x for x in self.get_children()]
        for child in children:
            children = children + child.get_family_tree(already_visited=already_visited)

        return [self] + children

    def get_path_to_me(self):
        """
        Get a list of all parents of this category.

        :return: a list where the first category is a top level category and the next ones the children to the category
        where this function is called upon
        """
        if self.parent is None:
            return [self]
        else:
            return self.parent.get_path_to_me() + [self]


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
        timezone = pytz.timezone(settings.TIME_ZONE)
        remove_after = timezone.localize(
            datetime.datetime.now() - datetime.timedelta(minutes=15)
        )
        for mail_list in mail_lists.iterator():
            if mail_list.created <= remove_after:
                mail_list.user_information.delete()
                mail_list.delete()
