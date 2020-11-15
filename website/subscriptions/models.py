import os

from django.db import models
from users.models import UserInformation
import secrets
import datetime
import pytz
from django.conf import settings


TEMPLATE_FILE_DIRECTORY = "templates/"


def letter_template_filename(instance, _):
    """Get the template file name for a letter."""
    return template_filename(instance, "letter_template.html")


def email_template_filename(instance, _):
    """Get the template file name for an email."""
    return template_filename(instance, "email_template.txt")


def template_filename(instance, filename):
    """Get the template filename."""
    if type(instance) == Subscription:
        return TEMPLATE_FILE_DIRECTORY + "subscription/{}/{}".format(
            instance.slug, filename
        )
    elif type(instance) == SubscriptionCategory:
        return TEMPLATE_FILE_DIRECTORY + "subscription-category/{}/{}".format(
            instance.slug, filename
        )
    else:
        return TEMPLATE_FILE_DIRECTORY + "null/{}/{}".format(
            instance.slug if instance.slug is not None else instance, filename
        )


class Subscription(models.Model):
    """Subscription model."""

    name = models.CharField(max_length=1024, help_text="The name of the subscription.")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="The price per year for the subscription.",
    )
    support_email = models.EmailField(
        blank=True,
        null=True,
        help_text="The support email address for the subscription. If enabled in the website settings, this is also the"
        " email address where the deregister emails are sent to.",
    )
    support_reply_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="The reply number (Postbus) for the subscription provider (to send the customers letter to).",
    )
    support_postal_code = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="The postal code for the support reply number.",
    )
    support_city = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="The city for the support reply number.",
    )
    correspondence_address = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="The correspondence address of the subscription provider.",
    )
    correspondence_postal_code = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="The postal code for the correspondence address of the subscription provider.",
    )
    correspondence_city = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="The city for the correspondence address of the subscription provider.",
    )
    support_phone_number = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="The support phone number (not paid).",
    )
    cancellation_number = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="The cancellation number (possibly paid).",
    )
    amount_used = models.PositiveIntegerField(
        default=1,
        help_text="The amount of times the subscription was used at deregistering of customers.",
    )
    category = models.ForeignKey(
        "SubscriptionCategory", null=True, blank=True, on_delete=models.SET_NULL
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        max_length=100,
        help_text="The last part of the URL for the page of the subscription provider.",
    )

    letter_template = models.FileField(
        upload_to=letter_template_filename,
        null=True,
        blank=True,
        help_text="The template of the letter to generate. For more information about"
        " this please check the template help information.",
    )
    email_template_text = models.FileField(
        upload_to=email_template_filename,
        null=True,
        blank=True,
        help_text="The template of the email to generate (as text). For more information about"
        " this please check the template help information.",
    )

    def __str__(self):
        """
        Convert this object to string.

        :return: a string with the name of the subscription
        """
        return self.name

    def get_letter_template(self):
        """
        Get the letter template location of this object.

        :return: the template file location
        """
        if self.category is not None:
            if not self.letter_template:
                return self.category.get_letter_template()
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.letter_template))
        else:
            if not self.letter_template:
                return os.path.join(
                    settings.BASE_DIR,
                    "subscriptions/templates/pdf/deregister_letter.html",
                )
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.letter_template))

    def get_email_template_text(self):
        """
        Get the email template location of this object.

        :return: the template file location
        """
        if self.category is not None:
            if not self.email_template_text:
                return self.category.get_email_template_text()
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.email_template_text))
        else:
            if not self.email_template_text:
                return os.path.join(
                    settings.BASE_DIR,
                    "subscriptions/templates/email/deregister_mail.txt",
                )
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.email_template_text))

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

        if max_items > 0:
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

    def has_registered_price(self):
        """
        Check if a subscription has a registered price.

        :return: True if the price is registered in the database
        """
        return self.price is not None and self.price != 0

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
                self.support_reply_number_prefixed,
                self.support_postal_code,
                self.support_city,
            )
        else:
            return (
                self.correspondence_address,
                self.correspondence_postal_code,
                self.correspondence_city,
            )

    @property
    def support_reply_number_prefixed(self):
        """
        Get the support reply number with prefix.

        :return: the support reply number with the prefix
        """
        return (
            "Postbus {}".format(self.support_reply_number)
            if self.support_reply_number is not None and self.support_reply_number != ""
            else self.support_reply_number
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
            "has_price": self.has_registered_price(),
            "slug": self.slug,
        }

    class Meta:
        """Meta class."""

        ordering = ["name"]


class SubscriptionCategory(models.Model):
    """Category for subscriptions."""

    name = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=100, null=False, blank=False, unique=True)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )

    letter_template = models.FileField(
        upload_to=letter_template_filename,
        null=True,
        blank=True,
        help_text="The template of the letter to generate. For more information about"
        " this please check the template help information.",
    )
    email_template_text = models.FileField(
        upload_to=email_template_filename,
        null=True,
        blank=True,
        help_text="The template of the email to generate (as text). For more information about"
        " this please check the template help information.",
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

    def get_letter_template(self):
        """
        Get the letter template location of this object.

        :return: the template file location
        """
        if self.parent is not None:
            if not self.letter_template:
                return self.parent.get_letter_template()
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.letter_template))
        else:
            if not self.letter_template:
                return os.path.join(
                    settings.BASE_DIR,
                    "subscriptions/templates/pdf/deregister_letter.html",
                )
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.letter_template))

    def get_email_template_text(self):
        """
        Get the email template location of this object.

        :return: the template file location
        """
        if self.parent is not None:
            if not self.email_template_text:
                return self.parent.get_email_template_text()
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.email_template_text))
        else:
            if not self.email_template_text:
                return os.path.join(
                    settings.BASE_DIR,
                    "subscriptions/templates/email/deregister_mail.txt",
                )
            else:
                return os.path.join(settings.MEDIA_ROOT, str(self.email_template_text))

    def get_subcategories(self, order="name"):
        """
        Get the subcategories of this category.

        :param order: how to order the subcategories
        :return: a QuerySet of SubscriptionCategory objects
        """
        subcategories = SubscriptionCategory.objects.filter(parent=self).order_by(order)
        return subcategories

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
