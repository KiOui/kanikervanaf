import threading
import requests
import json
import html
from django.views.generic import TemplateView
from subscriptions.models import Subscription, SubscriptionCategory
from django.shortcuts import render
from django.template.defaultfilters import slugify
import logging

logger = logging.getLogger(__name__)


class ImportFromWebsite(TemplateView):
    """View for starting the import process from a Wordpress hosted website with the deregister plugin."""

    def get(self, request, **kwargs):
        """
        GET request for the import view.

        :param request: the request of the user
        :param kwargs: keyword arguments
        :return: a render of the import.html page
        """
        return render(request, "import.html")

    def post(self, request, **kwargs):
        """
        POST request for the import view.

        This function starts the import_all function which starts the import process.
        :param request: the request of the user
        :param kwargs: keyword arguments
        :return: a render of the import.html page
        """
        import_url = request.POST.get('import-url')
        t = threading.Thread(target=import_all, args=(import_url,))
        t.start()
        context = {"started": True}
        return render(request, "import.html", context)


def import_all(import_url):
    """
    Start the import from a Wordpress hosted website with the deregister plugin.

    The import url can be set in the settings file of the website
    :return: None
    """
    logger.info("Starting import for {}".format(import_url))
    logger.info("Starting category import...")
    import_categories(import_url)
    logger.info("Category import done!")

    logger.info("Starting item import...")
    import_items(import_url)
    logger.info("Item import done!")


def import_items(import_url):
    """
    Start the import of the subscriptions in the Wordpress database.

    Items that are already in the Django database won't be imported
    :return: None
    """
    r = requests.post(
        import_url,
        data={"action": "deregister_categories", "option": "details_all"},
    )
    data = json.loads(html.unescape(r.text))
    for index, object in enumerate(data):
        logger.info("Completed {}/{}".format(index, len(data) - 1))
        if Subscription.objects.filter(name=object["name"]).count() == 0:
            try:
                import_item(object)
                logger.info("Imported {} successfully".format(object["name"]))
            except Exception as e:
                logger.error("Import failed for {}".format(object["name"]))
                logger.error(e)
        else:
            logger.info("Already imported {}".format(object["name"]))


def import_categories(import_url, category=False):
    """
    Start the import of the categories in the Wordpress database.

    This function will recursively call itself when encountering new categories
    :param import_url the url to import from
    :param category: the parent category, items requested from this category will be automatically placed under this
    parent
    :return: None
    """
    if category:
        r = requests.post(
            import_url,
            data={
                "action": "deregister_categories",
                "option": "childs",
                "category": category,
            },
        )
    else:
        r = requests.post(
            import_url,
            data={"action": "deregister_categories", "option": "childs"},
        )
    data = json.loads(html.unescape(r.text))
    for new_category in data:
        if SubscriptionCategory.objects.filter(name=new_category).count() == 0:
            if category:
                add_category(new_category, parent=category)
                import_categories(import_url, category=new_category)
            else:
                add_category(new_category)
                import_categories(import_url, category=new_category)
        else:
            logger.info("Category {} already in the database".format(new_category))
            import_categories(import_url, category=new_category)


def add_category(category_name, parent=False):
    """
    Add a category to the Django database.

    :param category_name: the name of the category to add
    :param parent: the parent of the category to add
    :return: None
    """
    if parent:
        SubscriptionCategory.objects.create(
            name=category_name,
            slug=slugify(category_name),
            parent=SubscriptionCategory.objects.get(name=parent),
        )
    else:
        SubscriptionCategory.objects.create(
            name=category_name, slug=slugify(category_name),
        )
    if parent:
        logger.info("Added {} under {}".format(category_name, parent))
    else:
        logger.info("Added {} as top level category".format(category_name))


def import_item(object):
    """
    Import one subscription into the Django database.

    If this function encounters that an item is associated with multiple categories, it will pick the first one that is
    not a top-level category.
    :param object: the object to import
    :return: None
    """
    categories = object["categories"]

    if len(categories) == 1:
        category = categories[0]
        Subscription.objects.create(
            name=object["name"],
            price=object["price"],
            support_email=object["mail"],
            support_reply_number=object["mail_answer_number"],
            support_postal_code=object["mail_postal_code"],
            support_city=object["mail_city"],
            correspondence_address=object["correspondence_address"],
            correspondence_postal_code=object["correspondence_postal_code"],
            correspondence_city=object["correspondence_city"],
            support_phone_number=object["phone_number"],
            cancellation_number=object["phone_number_free"],
            amount_used=object["used"],
            category=SubscriptionCategory.objects.get(name=category),
        )
    elif len(categories) > 1:
        logger.info(
            "Found multiple categories for {}\nNamely: {}".format(
                object["name"], categories
            )
        )
        category = categories[0]
        for c in categories:
            obj = SubscriptionCategory.objects.get(name=c)
            if obj.parent is not None:
                category = c
                break
        logger.info("Choosing {}".format(category))
        Subscription.objects.create(
            name=object["name"],
            price=object["price"],
            support_email=object["mail"],
            support_reply_number=object["mail_answer_number"],
            support_postal_code=object["mail_postal_code"],
            support_city=object["mail_city"],
            correspondence_address=object["correspondence_address"],
            correspondence_postal_code=object["correspondence_postal_code"],
            correspondence_city=object["correspondence_city"],
            support_phone_number=object["phone_number"],
            cancellation_number=object["phone_number_free"],
            amount_used=object["used"],
            category=SubscriptionCategory.objects.get(name=category),
        )
    else:
        Subscription.objects.create(
            name=object["name"],
            price=object["price"],
            support_email=object["mail"],
            support_reply_number=object["mail_answer_number"],
            support_postal_code=object["mail_postal_code"],
            support_city=object["mail_city"],
            correspondence_address=object["correspondence_address"],
            correspondence_postal_code=object["correspondence_postal_code"],
            correspondence_city=object["correspondence_city"],
            support_phone_number=object["phone_number"],
            cancellation_number=object["phone_number_free"],
            amount_used=object["used"],
        )
