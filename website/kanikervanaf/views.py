from django.shortcuts import render
from django.views.generic import TemplateView
from mail.services import send_contact_email
from .forms import ContactForm


class IndexView(TemplateView):
    """Home view."""

    template_name = "kanikervanaf/index.html"


class FAQView(TemplateView):
    """Frequently asked questions view."""

    template_name = "kanikervanaf/faq.html"


class PrivacyPolicy(TemplateView):
    """Frequently asked questions view."""

    template_name = "kanikervanaf/privacy.html"


class ContactView(TemplateView):
    """Contact view."""

    template_name = "kanikervanaf/contact.html"

    def get(self, request, **kwargs):
        """
        GET request function for request view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: the contact.html page
        """
        form = ContactForm(None)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request function for the request view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the contact.html page, either with a succeeded or failed message indicating if the request
        was send successfully or not
        """
        form = ContactForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email")
            title = form.cleaned_data.get("title")
            message = form.cleaned_data.get("content")
            context["form"] = ContactForm(None)
            if send_contact_email(name, email, title, message, request):
                context["succeeded"] = True
                return render(request, self.template_name, context)
            else:
                context["failed"] = True
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, context)


def handler404(request, exception):
    """
    Handle a 404 (page not found) exception.

    :param request: the request
    :param exception: the exception
    :return: a render of the 404 page
    """
    return render(request, "kanikervanaf/404.html", status=404)


def handler500(request):
    """
    Handle a 50x (server fault) exception.

    :param request: the request
    :return: a render of the 500 page
    """
    return render(request, "kanikervanaf/500.html", status=500)
