from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class FAQSitemap(Sitemap):
    """Sitemap for FAQView."""

    changefreq = "never"
    priority = 0.1

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["faq"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class PrivacySitemap(Sitemap):
    """Sitemap for PrivacyView."""

    changefreq = "never"
    priority = 0.1

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["privacy"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class ContactSitemap(Sitemap):
    """Sitemap for ContactView."""

    changefreq = "never"
    priority = 0.2

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["contact"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class HomeSitemap(Sitemap):
    """Sitemap for HomeView."""

    changefreq = "never"
    priority = 1

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["home"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)
