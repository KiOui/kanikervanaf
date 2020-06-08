from django.contrib.sitemaps import Sitemap
from django.core.paginator import Paginator
from django.urls import reverse
from posts.models import Post, STATUS_PUBLISHED
from posts.views import PostDetailsView, PostOverviewView


class PostOverviewSitemap(Sitemap):
    """Sitemap for PostOverviewView."""

    changefreq = "daily"
    priority = 0.6

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of pages
        """
        posts = Post.objects.filter(status=STATUS_PUBLISHED, response_to=None)
        paginator = Paginator(posts, PostOverviewView.paginate_by)
        return range(1, paginator.num_pages + 1)

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse("posts:post_overview", kwargs={"page": obj})


class PostCreateSitemap(Sitemap):
    """Sitemap for PostCreateView."""

    changefreq = "never"
    priority = 0.2

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of urls
        """
        return ["posts:post_create"]

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        return reverse(obj)


class PostDetailsSitemap(Sitemap):
    """Sitemap for PostDetailsView."""

    changefreq = "daily"
    priority = 0.7

    def items(self):
        """
        Get a list of items corresponding to this sitemap.

        :return: a list of (post, page) pairs
        """
        posts = Post.objects.filter(status=STATUS_PUBLISHED)
        pages = list()
        for post in posts:
            reactions = Post.objects.filter(response_to=post, status=STATUS_PUBLISHED)
            paginator = Paginator(reactions, PostDetailsView.paginate_by)
            for i in range(1, paginator.num_pages + 1):
                pages.append((post, i))
        return pages

    def location(self, obj):
        """
        Get the location of an object for this sitemap.

        :param obj: the object to get the location for
        :return: the relative url to the objects location on this site
        """
        post, page = obj
        return reverse("posts:details", kwargs={"post": post, "page": page})

    def lastmod(self, obj):
        """
        Get the date when this object was last modified.

        :param obj: the object
        :return: a date value when this object was last modified
        """
        post, page = obj
        return post.updated_on
