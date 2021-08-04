import urllib.parse
import json

from django.core.paginator import Paginator
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    Http404,
    HttpResponseForbidden,
)

from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Subscription, SubscriptionCategory, QueuedMailList
from django.db.models import Q
from .services import (
    handle_verification_request,
    handle_deregister_request,
)
from django.urls import reverse
from subscriptions.services import send_verification_email, send_request_email
from .forms import RequestForm, EnterUserInformationForm
import logging
from django.http import HttpResponsePermanentRedirect
import json
from urllib.parse import unquote_plus

logger = logging.getLogger(__name__)


class BasicUserInformation(TemplateView):
    """View for entering user information."""

    cookie_name = "subscription_details"

    template_name = "subscriptions/enter_information.html"

    def _is_cookie_empty(self, cookie):
        if cookie is not None:
            try:
                loaded_data = json.loads(unquote_plus(cookie))
            except json.JSONDecodeError:
                return True
            if type(loaded_data) == dict:
                for key in loaded_data.keys():
                    if bool(loaded_data[key]):
                        return False
        return True

    def get(self, request, **kwargs):
        """
        GET request for user information view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: render of the enter_information page
        """
        if request.user.is_authenticated and self._is_cookie_empty(
            request.COOKIES.get("subscription_details", None)
        ):
            return render(
                request,
                self.template_name,
                {"form": EnterUserInformationForm(user=request.user)},
            )
        else:
            return render(
                request, self.template_name, {"form": EnterUserInformationForm()}
            )


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
        top_level_categories = SubscriptionCategory.get_top_level_categories().order_by(
            "order"
        )
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
        category = kwargs.get("category")
        category_path = category.get_path_to_me()
        subcategories = category.get_subcategories()
        if subcategories.count() > 0:
            category.subcategories = subcategories
        category.top = Subscription.top_category(category, max_items=0, order_by="name")
        return render(
            request,
            self.template_name,
            {"category": category, "category_path": category_path},
        )


class ListCategoryRedirectView(TemplateView):
    """Redirects old list category view to the new one."""

    def get(self, request, **kwargs):
        """
        GET request for ListCategoryRedirectView.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the new page with the slug
        """
        category_int = kwargs.get("category")
        try:
            category = SubscriptionCategory.objects.get(id=category_int)
        except SubscriptionCategory.DoesNotExist:
            raise Http404("This subscription category does not exist")
        return HttpResponsePermanentRedirect(
            reverse("subscriptions:overview_category", kwargs={"category": category})
        )


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
        category = kwargs.get("category")
        category_path = category.get_path_to_me()
        subcategories = category.get_subcategories()
        if subcategories.count() > 0:
            category.subcategories = subcategories
        subscriptions = Subscription.top_category(
            category, max_items=0, order_by="name"
        )
        page = kwargs.get("page")
        paginator = Paginator(subscriptions, self.paginate_by)
        if page not in paginator.page_range:
            raise Http404("Page not found")
        category.top = paginator.get_page(page)
        return render(
            request,
            self.template_name,
            {"category": category, "category_path": category_path},
        )


class ListCategoryPageRedirectView(TemplateView):
    """Redirects old list category page view to the new one."""

    def get(self, request, **kwargs):
        """
        GET request for ListCategoryPageRedirectView.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the new page with the slug
        """
        category_int = kwargs.get("category")
        page = kwargs.get("page")
        try:
            category = SubscriptionCategory.objects.get(id=category_int)
        except SubscriptionCategory.DoesNotExist:
            raise Http404("This subscription category does not exist")
        return HttpResponsePermanentRedirect(
            reverse(
                "subscriptions:overview_category_page",
                kwargs={"category": category, "page": page},
            )
        )


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
            urllib.parse.unquote(request.COOKIES.get("subscription_details", ""))
        )
        items = json.loads(
            urllib.parse.unquote(request.COOKIES.get("subscription_items", ""))
        )
    except Exception as e:
        return HttpResponseRedirect(reverse("subscriptions:verification_send_failed"))

    mail_list = handle_verification_request(details, items)
    if mail_list:
        verification_url = request.build_absolute_uri(
            reverse("subscriptions:verify", kwargs={"token": mail_list.token})
        )
        if send_verification_email(
            mail_list.firstname,
            mail_list.email_address,
            verification_url,
        ):
            response = HttpResponseRedirect(
                reverse("subscriptions:verification_send_succeeded")
            )
            response.delete_cookie("subscription_details")
            response.delete_cookie("subscription_items")
            return response
        else:
            mail_list.delete()
            return HttpResponseRedirect(
                reverse("subscriptions:verification_send_failed")
            )
    else:
        return HttpResponseRedirect(reverse("subscriptions:verification_send_failed"))


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
        initial = {
            "subscription_name": request.GET.get("subscription", None),
            "name": request.user.get_full_name()
            if request.user.is_authenticated
            else None,
            "email": request.user.email if request.user.is_authenticated else None,
        }
        form = RequestForm(initial=initial)
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


class SubscriptionDetailsRedirectView(TemplateView):
    """Redirect old subscription details pages."""

    def get(self, request, **kwargs):
        """
        GET request for SubscriptionDetailsRedirectView.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the new page with the slug
        """
        subscription_int = kwargs.get("subscription")
        try:
            subscription = Subscription.objects.get(id=subscription_int)
        except Subscription.DoesNotExist:
            raise Http404("This subscription does not exist")
        return HttpResponsePermanentRedirect(
            reverse("subscriptions:details", kwargs={"subscription": subscription})
        )


def verify(request, **kwargs):
    """
    Verify a verification request.

    :param request: the request to verify
    :param kwargs: keyword arguments
    :return: a rendered page with either a succeeded message or failed message regarding the verification
    """
    token = kwargs.get("token", "")
    try:
        mail_list = QueuedMailList.objects.get(token=token)
    except QueuedMailList.DoesNotExist:
        raise Http404()

    if handle_deregister_request(mail_list):
        return render(request, "subscriptions/mails_send.html", {"succeeded": True})
    else:
        return render(request, "subscriptions/mails_send.html", {"succeeded": False})


class VerificationSendSucceeded(TemplateView):
    """Template for send verification."""

    template_name = "subscriptions/verification_send.html"

    def get(self, request, **kwargs):
        """
        GET request handler.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the verification_send.html page with a succeeded message
        """
        return render(request, self.template_name, {"succeeded": True})


class VerificationSendFailed(TemplateView):
    """Template for failed verification send."""

    template_name = "subscriptions/verification_send.html"

    def get(self, request, **kwargs):
        """
        GET request handler.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the verification_send.html page with a failed message
        """
        return render(request, self.template_name, {"succeeded": False})


class AdminTemplateInformationView(TemplateView):
    """Admin template information view."""

    template_name = "subscriptions/admin_template_explanation.html"

    def get(self, request, **kwargs):
        """Render the admin template information view."""
        if request.user and request.user.is_staff:
            return render(request, self.template_name)
        else:
            return HttpResponseForbidden()
