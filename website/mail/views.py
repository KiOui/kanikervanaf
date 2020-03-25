from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views.generic import TemplateView
from subscriptions.models import QueuedMailList
from .services import handle_deregister_request


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
        return HttpResponseNotFound()

    if handle_deregister_request(mail_list):
        return render(request, "mails_send.html", {"succeeded": True})
    else:
        return render(request, "mails_send.html", {"succeeded": False})


class VerificationSendSucceeded(TemplateView):
    """Template for send verification."""

    template_name = "verification_send.html"

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

    template_name = "verification_send.html"

    def get(self, request, **kwargs):
        """
        GET request handler.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the verification_send.html page with a failed message
        """
        return render(request, self.template_name, {"succeeded": False})
