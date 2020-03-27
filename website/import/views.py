import threading
import requests
import json
import html
from django.views.generic import TemplateView
from subscriptions.models import Subscription, SubscriptionCategory
from django.conf import settings
from django.shortcuts import render
from django.template.defaultfilters import slugify


class ImportFromWebsite(TemplateView):
    """View for starting the import process from a Wordpress hosted website with the deregister plugin."""

    def get(self, request, **kwargs):
        """
        GET request for the import view.

        This function starts the import_all function which starts the import process.
        :param request: the request of the user
        :param kwargs: keyword arguments
        :return: a render of the import.html page
        """
        t = threading.Thread(target=import_all)
        t.start()
        return render(request, "import.html")


def import_all():
    """
    Start the import from a Wordpress hosted website with the deregister plugin.

    The import url can be set in the settings file of the website
    :return: None
    """
    print("Starting import...")
    print("Starting category import...")
    import_categories(False)
    print("Category import done!")

    print("Starting item import...")
    r = requests.post(
        settings.IMPORT_URL, data={"action": "deregister_categories", "option": "all"}
    )
    names = json.loads(html.unescape(r.text))
    print("Got all names from the server!")
    print("Importing them now in the background")
    import_items(names)
    print("Item import done!")


def import_items(names):
    """
    Start the import of the subscriptions in the Wordpress database.

    Items that are already in the Django database won't be imported
    :param names: the names of the items to import
    :return: None
    """
    for index, name in enumerate(names):
        print("Completed {}/{}".format(index, len(names) - 1))
        if Subscription.objects.filter(name=name).count() == 0:
            try:
                import_item(name)
                print("Imported {} successfully".format(name))
            except Exception as e:
                print("Import failed for {}".format(name))
                print(e)
        else:
            print("Already imported {}".format(name))


def import_categories(category=False):
    """
    Start the import of the categories in the Wordpress database.

    This function will recursively call itself when encountering new categories
    :param category: the parent category, items requested from this category will be automatically placed under this
    parent
    :return: None
    """
    if category:
        r = requests.post(
            settings.IMPORT_URL,
            data={
                "action": "deregister_categories",
                "option": "childs",
                "category": category,
            },
        )
    else:
        r = requests.post(
            settings.IMPORT_URL,
            data={"action": "deregister_categories", "option": "childs"},
        )
    data = json.loads(html.unescape(r.text))
    for new_category in data:
        if SubscriptionCategory.objects.filter(name=new_category).count() == 0:
            if category:
                add_category(new_category, parent=category)
                import_categories(category=new_category)
            else:
                add_category(new_category)
                import_categories(category=new_category)
        else:
            print("Category {} already in the database".format(new_category))
            import_categories(category=new_category)


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
        print("Added {} under {}".format(category_name, parent))
    else:
        print("Added {} as top level category".format(category_name))


def import_item(name):
    """
    Import one subscription into the Django database.

    If this function encounters that an item is associated with multiple categories, it will pick the first one that is
    not a top-level category.
    :param name: the name of the item to import
    :return: None
    """
    r = requests.post(
        settings.IMPORT_URL,
        data={"action": "deregister_categories", "option": "details", "name": name},
    )
    data = json.loads(html.unescape(r.text))
    r = requests.post(
        settings.IMPORT_URL,
        data={"action": "deregister_categories", "option": "category_of", "name": name},
    )
    categories = json.loads(html.unescape(r.text))

    if len(categories) == 1:
        category = categories[0]
        Subscription.objects.create(
            name=data["name"],
            price=data["price"],
            support_email=data["mail"],
            support_reply_number=data["mail_answer_number"],
            support_postal_code=data["mail_postal_code"],
            support_city=data["mail_city"],
            correspondence_address=data["correspondence_address"],
            correspondence_postal_code=data["correspondence_postal_code"],
            correspondence_city=data["correspondence_city"],
            support_phone_number=data["phone_number"],
            cancellation_number=data["phone_number_free"],
            amount_used=data["used"],
            category=SubscriptionCategory.objects.get(name=category),
        )
    elif len(categories) > 1:
        print("Found multiple categories for {}\nNamely: {}".format(name, categories))
        category = categories[0]
        for c in categories:
            obj = SubscriptionCategory.objects.get(name=c)
            if obj.parent is not None:
                category = c
                break
        print("Choosing {}".format(category))
        Subscription.objects.create(
            name=data["name"],
            price=data["price"],
            support_email=data["mail"],
            support_reply_number=data["mail_answer_number"],
            support_postal_code=data["mail_postal_code"],
            support_city=data["mail_city"],
            correspondence_address=data["correspondence_address"],
            correspondence_postal_code=data["correspondence_postal_code"],
            correspondence_city=data["correspondence_city"],
            support_phone_number=data["phone_number"],
            cancellation_number=data["phone_number_free"],
            amount_used=data["used"],
            category=SubscriptionCategory.objects.get(name=category),
        )
    else:
        Subscription.objects.create(
            name=data["name"],
            price=data["price"],
            support_email=data["mail"],
            support_reply_number=data["mail_answer_number"],
            support_postal_code=data["mail_postal_code"],
            support_city=data["mail_city"],
            correspondence_address=data["correspondence_address"],
            correspondence_postal_code=data["correspondence_postal_code"],
            correspondence_city=data["correspondence_city"],
            support_phone_number=data["phone_number"],
            cancellation_number=data["phone_number_free"],
            amount_used=data["used"],
        )
