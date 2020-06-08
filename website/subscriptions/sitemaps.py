from django.contrib.sitemaps import Sitemap
from django.core.paginator import Paginator
from django.urls import reverse
from subscriptions.models import Subscription, SubscriptionCategory
from subscriptions.views import ListCategoryPageView


class SubscriptionListSitemap(Sitemap):
    """Sitemap for SubscriptionListView."""

    changefreq = "weekly"
    priority = 1

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["subscriptions:overview"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class SubscriptionCategoryPageSitemap(Sitemap):
    """Sitemap for SubscriptionCategoryPageView."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of (category, page) pairs
        """
        categories = SubscriptionCategory.objects.all()
        pages = list()
        for category in categories:
            subscriptions = Subscription.objects.filter(category=category).order_by(
                "name"
            )
            paginator = Paginator(subscriptions, ListCategoryPageView.paginate_by)
            for i in range(1, paginator.num_pages + 1):
                pages.append((category, i))
        return pages

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        category, page = obj
        return reverse(
            "subscriptions:overview_category_page",
            kwargs={"id": category.id, "page": page},
        )


class SubscriptionSummarySitemap(Sitemap):
    """Sitemap for SubscriptionSummaryView."""

    changefreq = "never"
    priority = 0.1

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["subscriptions:summary"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class SubscriptionRequestSitemap(Sitemap):
    """Sitemap for SubscriptionRequestView."""

    changefreq = "never"
    priority = 0.3

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["subscriptions:request"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class SubscriptionDetailsSearchSitemap(Sitemap):
    """Sitemap for SubscriptionDetailsSearchView."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["subscriptions:details_search"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class SubscriptionDetailsSitemap(Sitemap):
    """Sitemap for SubscriptionDetailsView."""

    changefreq = "monthly"
    priority = 0.8

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of subscription objects
        """
        return Subscription.objects.all().order_by("name")

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse("subscriptions:details", kwargs={"subscription": obj})
