from django.shortcuts import render
from django.views.generic import TemplateView
from mail.services import send_contact_email


class IndexView(TemplateView):
    """Home view."""

    template_name = "index.html"


class FAQView(TemplateView):
    """Frequently asked questions view."""

    template_name = "faq.html"


class ContactView(TemplateView):
    """Contact view."""

    template_name = "contact.html"

    def get(self, request, **kwargs):
        """
        GET request function for request view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: the contact.html page
        """
        return render(request, self.template_name)

    def post(self, request, **kwargs):
        """
        POST request function for the request view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the contact.html page, either with a succeeded or failed message indicating if the request
        was send successfully or not
        """
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        title = request.POST.get("title", "")
        message = request.POST.get("message", "")

        if send_contact_email(name, email, title, message):
            return render(request, self.template_name, {"succeeded": True})
        else:
            return render(request, self.template_name, {"failed": True})
