import urllib.parse
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Subscription, SubscriptionCategory
from .services import handle_verification_request
from django.urls import reverse
from mail.services import send_verification_email


class ListView(TemplateView):
    """List view for subscriptions."""

    template_name = "subscription_select.html"

    def get(self, request, **kwargs):
        """
        GET request function for list view.

        Creates a list of top-level categories and their top five used subscription items.
        :param request: the request
        :param kwargs: keyword arguments
        :return: the subscription_select.html page with a top five of all top-level categories
        """
        top_level_categories = SubscriptionCategory.get_top_level_categories()
        for category in top_level_categories:
            category.top = Subscription.top_category(category, order_by="-amount_used")
        return render(request, self.template_name, {"categories": top_level_categories})


class ListCategoryView(TemplateView):
    """List view for subscriptions of a specific category."""

    template_name = "subscription_category.html"

    def get(self, request, **kwargs):
        """
        GET request function for list category view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: the subscription_category.html page with all subscriptions belonging to a specific category
        """
        if SubscriptionCategory.objects.filter(id=kwargs.get("id")).count() > 0:
            category = SubscriptionCategory.objects.get(id=kwargs.get("id"))
            category.top = Subscription.top_category(category, max_items=0)
            for item in category.top:
                item.can_email = item.can_email()
                item.can_generate_pdf = item.can_generate_pdf()
            return render(request, self.template_name, {"category": category})
        else:
            return redirect("subscriptions:overview")


class SummaryView(TemplateView):
    """Summary view of the selected subscriptions."""

    template_name = "summary.html"


def verification_send(request):
    """
    Send a verification request.

    :param request: the verification request
    :return: either a HttpResponseRedirect redirecting to a succeeded or failed page or a HttpResponse 500 if a COOKIE
    could not be parsed or the QueuedMailList couldn't be constructed
    """
    try:
        details = json.loads(
            urllib.parse.unquote(request.COOKIES.get("subscription_details"))
        )
        items = json.loads(
            urllib.parse.unquote(request.COOKIES.get("subscription_items"))
        )
    except ValueError:
        return HttpResponse(status=500)

    mail_list = handle_verification_request(details, items)
    if mail_list:
        verification_url = request.build_absolute_uri(
            reverse("mail:verify", kwargs={"token": mail_list.token})
        )
        if send_verification_email(
            mail_list.user_information.firstname,
            mail_list.user_information.email_address,
            verification_url,
        ):
            return HttpResponseRedirect(reverse("mail:verification_send_succeeded"))
        else:
            mail_list.user_information.delete()
            mail_list.delete()
            return HttpResponseRedirect(reverse("mail:verification_send_failed"))
    else:
        return HttpResponse(status=500)
