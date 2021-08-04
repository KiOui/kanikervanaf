import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from django.http import (
    Http404,
    FileResponse,
)

from subscriptions.models import Subscription, SubscriptionCategory
from subscriptions.services import get_file_contents


class SubscriptionLetterTemplateEditorView(PermissionRequiredMixin, TemplateView):
    """Subscription letter template editor."""

    permission_required = "is_staff"
    template_name = "subscriptions/admin/template_editor.html"
    app_label = "subscriptions"
    instance_type = Subscription
    accepts = "application/pdf"
    view_name = "Letter Template editor"

    def get(self, request, **kwargs):
        """Get request."""
        instance = self.get_instance_obj()
        saved_template = self.get_saved_template()
        (
            address,
            postal_code,
            city,
        ) = self.get_default_address_information()
        return render(
            request,
            self.template_name,
            {
                "view_name": self.view_name,
                "instance_name": instance.name,
                "instance_address": address,
                "instance_postal_code": postal_code,
                "instance_city": city,
                "accepts": self.accepts,
                "date": datetime.datetime.now().strftime("%d-%m-%Y"),
                "saved_template": saved_template,
                "site_title": site.site_title,
                "opts": self.instance_type._meta,
                "original": instance,
                "has_view_permission": site.has_permission(request),
                "site_header": site.site_header,
                "site_url": site.site_url,
                "app_label": self.app_label,
                "is_popup": False,
                "is_nav_sidebar_enabled": site.enable_nav_sidebar,
                "available_apps": site.get_app_list(request),
            },
        )

    def post(self, request, **kwargs):
        """Post request."""
        instance = self.get_instance_obj()
        saved_template = self.get_saved_template()
        (
            address,
            postal_code,
            city,
        ) = self.get_default_address_information()
        if "source" in request.POST.keys():
            self.save(request.POST["source"])
            return render(
                request,
                self.template_name,
                {
                    "saved": True,
                    "view_name": self.view_name,
                    "instance_name": instance.name,
                    "instance_address": address,
                    "instance_postal_code": postal_code,
                    "instance_city": city,
                    "accepts": self.accepts,
                    "date": datetime.datetime.now().strftime("%d-%m-%Y"),
                    "saved_template": saved_template,
                    "site_title": site.site_title,
                    "opts": self.instance_type._meta,
                    "original": instance,
                    "has_view_permission": site.has_permission(request),
                    "site_header": site.site_header,
                    "site_url": site.site_url,
                    "app_label": self.app_label,
                    "is_popup": False,
                    "is_nav_sidebar_enabled": site.enable_nav_sidebar,
                    "available_apps": site.get_app_list(request),
                },
            )
        else:
            return render(
                request,
                self.template_name,
                {
                    "error": True,
                    "view_name": self.view_name,
                    "instance_name": instance.name,
                    "instance_address": address,
                    "instance_postal_code": postal_code,
                    "instance_city": city,
                    "accepts": self.accepts,
                    "date": datetime.datetime.now().strftime("%d-%m-%Y"),
                    "saved_template": saved_template,
                    "site_title": site.site_title,
                    "opts": self.instance_type._meta,
                    "original": instance,
                    "has_view_permission": site.has_permission(request),
                    "site_header": site.site_header,
                    "site_url": site.site_url,
                    "app_label": self.app_label,
                    "is_popup": False,
                    "is_nav_sidebar_enabled": site.enable_nav_sidebar,
                    "available_apps": site.get_app_list(request),
                },
            )

    def get_instance_obj(self):
        """Get instance."""
        return self.kwargs.get("instance")

    def save(self, source):
        """Save file contents."""
        self.get_instance_obj().letter_template.save("", ContentFile(source))

    def get_saved_template(self):
        """Get saved template pdf."""
        return (
            get_file_contents(self.get_instance_obj().letter_template_full_path)
            if self.get_instance_obj().letter_template_full_path is not None
            else ""
        )

    def get_default_address_information(self):
        """Get address information."""
        return self.get_instance_obj().get_address_information()


class SubscriptionEmailTemplateEditorView(SubscriptionLetterTemplateEditorView):
    """Subscription email template editor."""

    accepts = "text/plain"
    view_name = "Email Template editor"

    def get_saved_template(self):
        """Get saved template email."""
        return (
            get_file_contents(self.get_instance_obj().email_template_text_full_path)
            if self.get_instance_obj().email_template_text_full_path is not None
            else ""
        )

    def save(self, source):
        """Save file contents."""
        self.get_instance_obj().email_template_text.save("", ContentFile(source))


class SubscriptionCategoryLetterTemplateEditorView(
    SubscriptionLetterTemplateEditorView
):
    """Subscription Category letter template editor."""

    app_label = "subscription_categories"
    instance_type = SubscriptionCategory

    def get_default_address_information(self):
        """Get address information."""
        return "Aphroditestraat 37", "5047TW", "Tilburg"


class SubscriptionCategoryEmailTemplateEditorView(
    SubscriptionCategoryLetterTemplateEditorView
):
    """Subscription Category email template editor."""

    accepts = "text/plain"
    view_name = "Email Template editor"

    def get_saved_template(self):
        """Get saved template email."""
        return (
            get_file_contents(self.get_instance_obj().email_template_text_full_path)
            if self.get_instance_obj().email_template_text_full_path is not None
            else ""
        )

    def save(self, source):
        """Save file contents."""
        self.get_instance_obj().email_template_text.save("", ContentFile(source))


class AdminEmailTemplateView(PermissionRequiredMixin, TemplateView):
    """Get Email template file view."""

    permission_required = "is_staff"

    def get_file_handle(self):
        """Get file handle."""
        if self.kwargs.get("obj").email_template_text is not None:
            return self.kwargs.get("obj").email_template_text.open()
        else:
            return None

    def get(self, request, **kwargs):
        """Get an admin template file."""
        file_handle = self.get_file_handle()
        if file_handle is None:
            raise Http404()
        response = FileResponse(file_handle, content_type="text/plain")
        response["Content-Length"] = file_handle.size
        response["Content-Disposition"] = 'attachment; filename="%s"' % file_handle.name

        return response


class AdminLetterTemplateView(AdminEmailTemplateView):
    """Get Letter template file view."""

    def get_file_handle(self):
        """Get file handle."""
        if self.kwargs.get("obj").letter_template is not None:
            return self.kwargs.get("obj").letter_template.open()
        else:
            return None
