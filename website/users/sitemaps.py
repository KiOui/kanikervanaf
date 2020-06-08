from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class EnterUserSitemap(Sitemap):
    """Sitemap for EnterUserinformationView."""

    changefreq = "never"
    priority = 0.6

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["users:enter"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class UserSitemap(Sitemap):
    """Sitemap for the login, register and password forgot view."""

    changefreq = "never"
    priority = 0.2

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["users:login", "users:register", "users:forgot"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)
