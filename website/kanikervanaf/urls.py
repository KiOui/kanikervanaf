"""kanikervanaf URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import (
    IndexView,
    ContactView,
    FAQView,
    PrivacyPolicy,
    handler404 as custom_handler404,
    handler500 as custom_handler500,
)
from django.contrib.sitemaps.views import sitemap
from .sitemaps import HomeSitemap, ContactSitemap, FAQSitemap, PrivacySitemap
from posts.sitemaps import PostOverviewSitemap, PostCreateSitemap, PostDetailsSitemap
from subscriptions.sitemaps import (
    SubscriptionCategoryPageSitemap,
    SubscriptionListSitemap,
    SubscriptionDetailsSearchSitemap,
    SubscriptionDetailsSitemap,
    SubscriptionSummarySitemap,
    SubscriptionRequestSitemap,
    EnterUserSitemap,
)
from users.sitemaps import UserSitemap

sitemaps = {
    "home": HomeSitemap,
    "contact": ContactSitemap,
    "faq": FAQSitemap,
    "privacy": PrivacySitemap,
    "posts:post_create": PostCreateSitemap,
    "posts:post_overview": PostOverviewSitemap,
    "posts:details": PostDetailsSitemap,
    "subscriptions:overview": SubscriptionListSitemap,
    "subscriptions:overview_category_page": SubscriptionCategoryPageSitemap,
    "subscriptions:summary": SubscriptionSummarySitemap,
    "subscriptions:requets": SubscriptionRequestSitemap,
    "subscriptions:details_search": SubscriptionDetailsSearchSitemap,
    "subscriptions:details": SubscriptionDetailsSitemap,
    "subscriptions:enter": EnterUserSitemap,
    "users": UserSitemap,
}

handler404 = custom_handler404
handler500 = custom_handler500

urlpatterns = [
    path("tinymce/", include("tinymce.urls")),
    path("", IndexView.as_view(), name="home"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", include("robots.urls")),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("faq", FAQView.as_view(), name="faq"),
    path("privacybeleid", PrivacyPolicy.as_view(), name="privacy"),
    path("contact", ContactView.as_view(), name="contact"),
    path("admin/", admin.site.urls),
    path(
        "subscriptions/",
        include(("subscriptions.urls", "subscriptions"), namespace="subscriptions"),
    ),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("posts/", include(("posts.urls", "posts"), namespace="posts")),
    path("api/", include("kanikervanaf.api.urls")),
]
