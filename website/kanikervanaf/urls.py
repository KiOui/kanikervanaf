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
from .views import IndexView, ContactView, FAQView

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("faq", FAQView.as_view(), name="faq"),
    path("contact", ContactView.as_view(), name="contact"),
    path("admin/", admin.site.urls),
    path(
        "subscriptions/",
        include(("subscriptions.urls", "subscriptions"), namespace="subscriptions"),
    ),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("import/", include(("import.urls", "import"), namespace="import")),
    path("mail/", include(("mail.urls", "mail"), namespace="mail")),
    path("posts/", include(("posts.urls", "posts"), namespace="posts")),
]
