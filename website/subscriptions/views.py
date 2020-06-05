import urllib.parse
import json

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Subscription, SubscriptionCategory
from .services import handle_verification_request
from django.urls import reverse
from mail.services import send_verification_email, send_request_email
from .forms import RequestForm
import logging

logger = logging.getLogger(__name__)


class SubscriptionDetailsSearchView(TemplateView):
    """View for searching subscription details."""

    template_name = "subscriptions/subscription_details.html"

    def get(self, request, **kwargs):
        """
        GET request for Subscriptions details search view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the subscription_details page
        """
        top_subscriptions = Subscription.objects.all().order_by("-amount_used")[:20]
        return render(
            request, self.template_name, {"top_subscriptions": top_subscriptions}
        )


class SubscriptionDetailsView(TemplateView):
    """View for displaying the details of a subscription."""

    template_name = "subscriptions/subscription_details.html"

    def get(self, request, **kwargs):
        """
        GET request for Subscriptions details search view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the subscription_details page with details of a subscription
        """
        subscription = kwargs.get("subscription")
        top_subscriptions = Subscription.objects.all().order_by("-amount_used")[:20]
        return render(
            request,
            self.template_name,
            {"top_subscriptions": top_subscriptions, "subscription": subscription},
        )


class SubscriptionListView(TemplateView):
    """List view for subscriptions."""

    template_name = "subscriptions/subscription_select.html"

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

    template_name = "subscriptions/subscription_category.html"

    def get(self, request, **kwargs):
        """
        GET request function for list category view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: the subscription_category.html page with all subscriptions belonging to a specific category
        """
        if SubscriptionCategory.objects.filter(id=kwargs.get("id")).count() > 0:
            category = SubscriptionCategory.objects.get(id=kwargs.get("id"))
            category_path = category.get_path_to_me()
            subcategories = category.get_subcategories()
            if subcategories.count() > 0:
                category.subcategories = subcategories
            category.top = Subscription.top_category(
                category, max_items=0, order_by="name"
            )
            return render(
                request,
                self.template_name,
                {"category": category, "category_path": category_path},
            )
        else:
            return redirect("subscriptions:overview")


class ListCategoryPageView(TemplateView):
    """Category view with pages."""

    template_name = "subscriptions/subscription_category_page.html"
    paginate_by = 50

    def get(self, request, **kwargs):
        """
        GET request function for list category view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: the subscription_category.html page with all subscriptions belonging to a specific category
        """
        if SubscriptionCategory.objects.filter(id=kwargs.get("id")).count() > 0:
            category = SubscriptionCategory.objects.get(id=kwargs.get("id"))
            category_path = category.get_path_to_me()
            subcategories = category.get_subcategories()
            if subcategories.count() > 0:
                category.subcategories = subcategories
            subscriptions = Subscription.top_category(
                category, max_items=0, order_by="name"
            )
            page = kwargs.get("page")
            paginator = Paginator(subscriptions, self.paginate_by)
            category.top = paginator.get_page(page)
            return render(
                request,
                self.template_name,
                {"category": category, "category_path": category_path},
            )
        else:
            return redirect("subscriptions:overview")


class SummaryView(TemplateView):
    """Summary view of the selected subscriptions."""

    template_name = "subscriptions/summary.html"


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
    except ValueError as e:
        logger.error(e)
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


class RequestView(TemplateView):
    """Request view for sending in a subscription request."""

    template_name = "subscriptions/request.html"

    def get(self, request, **kwargs):
        """
        GET request function for request view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: the request.html page
        """
        form = RequestForm(None)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request function for the request view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the request.html page, either with a succeeded or failed message indicating if the request
        was send successfully or not
        """
        form = RequestForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email")
            subscription = form.cleaned_data.get("subscription_name")
            message = form.cleaned_data.get("content")
            context["form"] = RequestForm(None)
            if send_request_email(name, email, subscription, message):
                context["succeeded"] = True
                return render(request, self.template_name, context)
            else:
                context["failed"] = True
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, context)


def search_database(request):
    """
    Search all Subscription objects for a specific Subscription.

    :param request: the request, containing a POST parameter query
    :return: all objects
    """
    if request.method == "POST":
        query = request.POST.get("query", "")
        request_id = request.POST.get("id", "")
        try:
            maximum = int(request.POST.get("maximum", 5))
        except ValueError:
            maximum = 5
        subscriptions = Subscription.objects.filter(name__icontains=query).order_by(
            "-amount_used"
        )[:maximum]
        converted_set = convert_list_to_json(subscriptions)
        json_list = {"items": converted_set, "id": request_id}
        json_response = json.dumps(json_list)
        return HttpResponse(json_response, content_type="application/json")
    else:
        return HttpResponseRedirect(reverse("home"))


def convert_list_to_json(subscriptions):
    """
    Convert a list with subscriptions to a JSON compatible dictionary.

    :param subscriptions: a list of subscriptions to convert
    :return: a JSON string with the list of subscriptions converted to JSON
    """
    json_list = []
    for subscription in subscriptions:
        json_list.append(subscription.to_json())
    return json_list
