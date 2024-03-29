import os

from django.db import models
import secrets
import datetime
import pytz
from django.conf import settings
from tinymce.models import HTMLField
from ordered_model.models import OrderedModel


TEMPLATE_FILE_DIRECTORY = "templates/"


def letter_template_filename(instance, _):
    """Get the template file name for a letter."""
    return template_filename(instance, "letter_template.html")


def email_template_filename(instance, _):
    """Get the template file name for an email."""
    return template_filename(instance, "email_template.txt")


def template_filename(instance, filename):
    """Get the template filename."""
    if type(instance) == Subscription or type(instance) == SubscriptionCategory:
        return TEMPLATE_FILE_DIRECTORY + "{}/{}/{}".format(
            instance._meta.model_name, instance.slug, filename
        )
    else:
        raise Exception("There is no defined template filename for this model class")


class SubscriptionObject(models.Model):
    """Abstract model for overlapping Subscriptions and SubscriptionCategories."""

    name = models.CharField(max_length=512)
    slug = models.SlugField(unique=True, max_length=100)
    category = models.ForeignKey(
        "SubscriptionCategory", null=True, blank=True, on_delete=models.SET_NULL
    )
    letter_template = models.FileField(
        upload_to=letter_template_filename,
        null=True,
        blank=True,
        help_text="The template of the letter to generate.",
    )
    email_template_text = models.FileField(
        upload_to=email_template_filename,
        null=True,
        blank=True,
        help_text="The template of the email to generate (as text).",
    )

    class Meta:
        """Meta class."""

        unique_together = ("slug", "category")
        abstract = True

    def __str__(self):
        """
        Convert this object to string.

        :return: a string with the name of the subscription object
        """
        return self.name

    @property
    def letter_template_full_path(self):
        """Get full path letter template."""
        if self.letter_template:
            return os.path.join(settings.MEDIA_ROOT, str(self.letter_template))
        else:
            return None

    @property
    def email_template_text_full_path(self):
        """Get full path email template."""
        if self.email_template_text:
            return os.path.join(settings.MEDIA_ROOT, str(self.email_template_text))
        else:
            return None

    def get_letter_template(self):
        """
        Get the full path to the letter template location of this object.

        :return: the template file location
        """
        letter_template = self.letter_template_full_path
        if letter_template is not None:
            return letter_template
        elif self.category is not None:
            return self.category.get_letter_template()
        else:
            return os.path.join(
                settings.BASE_DIR,
                "subscriptions/templates/pdf/deregister_letter.html",
            )

    def get_email_template_text(self):
        """
        Get the email template location of this object.

        :return: the template file location
        """
        email_template = self.email_template_text_full_path
        if email_template is not None:
            return email_template
        elif self.category is not None:
            return self.category.get_email_template_text()
        else:
            return os.path.join(
                settings.BASE_DIR,
                "subscriptions/templates/email/deregister_mail.txt",
            )


class Subscription(SubscriptionObject):
    """Subscription model."""

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="The price per year for the subscription.",
    )
    support_email = models.EmailField(
        blank=True,
        default="",
        help_text=(
            "The support email address for the subscription. If enabled in the website"
            " settings, this is also the email address where the deregister emails are"
            " sent to."
        ),
    )
    support_reply_number = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text=(
            "The reply number (Postbus) for the subscription provider (to send the"
            " customers letter to)."
        ),
    )
    support_postal_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="The postal code for the support reply number.",
    )
    support_city = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="The city for the support reply number.",
    )
    correspondence_address = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="The correspondence address of the subscription provider.",
    )
    correspondence_postal_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=(
            "The postal code for the correspondence address of the subscription provider."
        ),
    )
    correspondence_city = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="The city for the correspondence address of the subscription provider.",
    )
    support_phone_number = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="The support phone number (not paid).",
    )
    cancellation_number = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="The cancellation number (possibly paid).",
    )
    amount_used = models.PositiveIntegerField(
        default=1,
        help_text="The amount of times the subscription was used at deregistering of customers.",
    )
    can_generate_letter = models.BooleanField(
        default=False,
        help_text="Whether or not this subscription can generate a deregistration letter.",
        editable=False,
    )
    can_generate_email = models.BooleanField(
        default=False,
        help_text="Whether or not this subscription can generate a deregistration email.",
        editable=False,
    )
    explanation_field = HTMLField(
        help_text="Possible explanation of how to deregister from this subscription if deregistering via email or "
        "letter is not possible.",
        blank=True,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]

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
        if self.support_reply_number != "" and self.support_postal_code != "":
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
            if self.support_reply_number != ""
            else ""
        )

    def deregistered(self):
        """
        Update the amount of times the subscription has been deregistered.

        Adds one to the amount of time this subscription has been used
        :return: None
        """
        self.amount_used += 1
        self.save()


class SubscriptionCategory(SubscriptionObject, OrderedModel):
    """Category for subscriptions."""

    order_with_respect_to = "category"

    class Meta:
        """Enforcing that there can not be two categories under a parent with same slug."""

        verbose_name = "Subscription category"
        verbose_name_plural = "Subscription categories"

    def get_subcategories(self, order="name"):
        """
        Get the subcategories of this category.

        :param order: how to order the subcategories
        :return: a QuerySet of SubscriptionCategory objects
        """
        subcategories = SubscriptionCategory.objects.filter(category=self).order_by(
            order
        )
        return subcategories

    @staticmethod
    def get_top_level_categories():
        """
        Get all top level categories (categories without parents).

        :return: a set with all top level categories
        """
        return SubscriptionCategory.objects.filter(category=None)

    def get_family_tree(self, already_visited=None):
        """
        Get all family members of a category.

        :param already_visited: against infinite recursion
        :return: a list with all family members of a category.
        """
        if already_visited is None:
            already_visited = []

        if self in already_visited:
            return []
        else:
            already_visited.append(self)

        children_visiting = [x for x in self.get_subcategories(order="id")]
        all_children = []
        for child in children_visiting:
            all_children = all_children + child.get_family_tree(
                already_visited=already_visited
            )

        return [self] + all_children

    def get_path_to_me(self):
        """
        Get a list of all parents of this category.

        :return: a list where the first category is a top level category and the next ones the children to the category
        where this function is called upon
        """
        if self.category is None:
            return [self]
        else:
            return self.category.get_path_to_me() + [self]


class SubscriptionSearchTerm(models.Model):
    """Additional search terms for a Subscription."""

    name = models.CharField(max_length=512)
    subscription = models.ManyToManyField("Subscription")

    def __str__(self):
        """
        Convert this object to a string.

        :return: a string with the name of the search term
        """
        return self.name


class QueuedMailList(models.Model):
    """Submitted user list with subscriptions to deregister from."""

    token = models.CharField(max_length=64, unique=True)
    item_list = models.ManyToManyField(Subscription)
    created = models.DateTimeField(auto_now_add=True)
    firstname = models.CharField(max_length=512)
    lastname = models.CharField(max_length=512, blank=True)
    email_address = models.EmailField(max_length=512)
    address = models.CharField(max_length=512, blank=True)
    postal_code = models.CharField(max_length=256, blank=True)
    residence = models.CharField(max_length=512, blank=True)

    def __str__(self):
        """
        Convert this object to a string.

        :return: a string with the token and the creation time
        """
        return "{}, created: {}".format(self.token, self.created)

    @staticmethod
    def generate(
        firstname: str,
        lastname: str,
        email_address: str,
        address: str,
        postal_code: str,
        residence: str,
        subscription_list: [Subscription],
    ):
        """
        Generate a new QueuedMailList by first creating a new random hexadecimal token of 32 bytes.

        :param firstname: User's first name
        :param lastname: User's last name (optional)
        :param email_address: User's email address
        :param address: User's address (optional)
        :param postal_code: User's postal code (optional)
        :param residence: User's residence (optional)
        :param subscription_list: list of Subscription objects to add to the Queued Mail list (Subscriptions the user
        wants to deregister from)
        :return: Created QueuedMailList with a fresh random token
        """
        random_token = secrets.token_hex(32)
        mail_list = QueuedMailList.objects.create(
            token=random_token,
            firstname=firstname,
            lastname=lastname,
            email_address=email_address,
            address=address,
            postal_code=postal_code,
            residence=residence,
        )
        for item in subscription_list:
            mail_list.item_list.add(item)
        return mail_list

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
                mail_list.delete()
