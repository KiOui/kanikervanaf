import datetime
import os

import django.template.exceptions
from django.conf import settings
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from kanikervanaf.api.openapi import CustomAutoSchema
from subscriptions.api.v1.pagination import StandardResultsSetPagination
from subscriptions.api.v1.renderers import PDFRenderer, PlainTextRenderer
from subscriptions.api.v1.serializers import (
    SubscriptionSerializer,
    SubscriptionCategorySerializer,
)
from subscriptions.models import Subscription, SubscriptionCategory
from subscriptions.services import (
    render_deregister_letter,
    create_deregister_email,
    render_string,
    render_string_to_pdf,
)
from users.models import UserInformation


class SubscriptionListAPIView(ListAPIView):
    """
    Subscription List API View.

    Permissions required: None

    Use this endpoint to get a list of subscriptions in the database.
    """

    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    pagination_class = StandardResultsSetPagination


class SubscriptionRetrieveAPIView(RetrieveAPIView):
    """
    Subscription Retrieve API View.

    Permission required: None

    Use this endpoint to get the details of a Subscription.
    """

    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()


class SubscriptionCategoryListAPIView(ListAPIView):
    """
    Subscription Category List API View.

    Permissions required: None

    Use this endpoint to get a list of subscription categories in the database.
    """

    serializer_class = SubscriptionCategorySerializer
    queryset = SubscriptionCategory.objects.all()
    pagination_class = StandardResultsSetPagination


class SubscriptionCategoryRetrieveAPIView(RetrieveAPIView):
    """
    Subscription Category Retrieve API View.

    Permission required: None

    Use this endpoint to get the details of a Subscription Category.
    """

    serializer_class = SubscriptionCategorySerializer
    queryset = SubscriptionCategory.objects.all()


class SubscriptionRenderLetterAPIView(APIView):
    """
    Subscription Render Letter API View.

    Permission required: None

    Use this endpoint to render the letter of a Subscription.
    """

    renderer_classes = [PDFRenderer]
    render_obj = Subscription
    render_obj_value_name = "letter_template"

    def get(self, request, **kwargs):
        """Get request."""
        try:
            instance = self.render_obj.objects.get(pk=kwargs.get("pk"))
        except self.render_obj.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if instance.__dict__[self.render_obj_value_name]:
            pdf = self.render(instance)
            return Response(
                status=status.HTTP_200_OK, data=pdf, content_type="application/pdf"
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def render(self, instance):
        """Render letter."""
        return render_deregister_letter(
            UserInformation.get_test_instance(),
            Subscription.get_test_instance(),
            os.path.join(
                settings.MEDIA_ROOT, str(instance.__dict__[self.render_obj_value_name])
            ),
        )


class SubscriptionRenderEmailAPIView(APIView):
    """
    Subscription Render Email API View.

    Permission required: None

    Use this endpoint to render the email of a Subscription.
    """

    renderer_classes = [PlainTextRenderer]
    render_obj = Subscription
    render_obj_value_name = "email_template_text"

    def get(self, request, **kwargs):
        """Get request."""
        try:
            instance = self.render_obj.objects.get(pk=kwargs.get("pk"))
        except self.render_obj.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if instance.__dict__[self.render_obj_value_name]:
            text = self.render(instance)
            return Response(
                status=status.HTTP_200_OK, data=text, content_type="text/plain"
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def render(self, instance):
        """Render email."""
        return create_deregister_email(
            UserInformation.get_test_instance(),
            Subscription.get_test_instance(),
            os.path.join(
                settings.MEDIA_ROOT, str(instance.__dict__[self.render_obj_value_name])
            ),
        )


class SubscriptionCategoryRenderLetterAPIView(SubscriptionRenderLetterAPIView):
    """
    Subscription Category Render Letter API View.

    Permission required: None

    Use this endpoint to render the letter of a SubscriptionCategory.
    """

    render_obj = SubscriptionCategory


class SubscriptionCategoryRenderEmailAPIView(SubscriptionRenderEmailAPIView):
    """
    Subscription Category Render Letter API View.

    Permission required: None

    Use this endpoint to render the email of a SubscriptionCategory.
    """

    render_obj = SubscriptionCategory


class TemplateAPIView(APIView):
    """
    Template API View.

    Permission required: is_staff

    Use this endpoint to render a user submitted template with a user submitted context.
    """

    schema = CustomAutoSchema(
        request_schema={
            "type": "object",
            "properties": {
                "source": {"type": "string", "example": "string"},
                "context": {"type": "object", "example": {"name": "string"}},
            },
        }
    )

    renderer_classes = [PDFRenderer, PlainTextRenderer]
    permission_classes = [IsAdminUser]

    def post(self, request, **kwargs):
        """Render user submitted template."""
        if "source" not in request.data.keys() or "context" not in request.data.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        context_data = {
            "date": datetime.datetime.now().strftime("%d-%m-%Y"),
        }
        context_data.update(request.data["context"])
        if request.accepted_renderer.format == "pdf":
            try:
                pdf = render_string_to_pdf(request.data["source"], context_data)
            except (
                django.template.exceptions.TemplateSyntaxError,
                django.template.exceptions.TemplateDoesNotExist,
            ) as e:
                request.accepted_renderer = JSONRenderer()
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"detail": e.__str__()},
                    content_type="application/json",
                )
            return Response(
                status=status.HTTP_200_OK, data=pdf, content_type="application/pdf"
            )
        else:
            try:
                text = render_string(request.data["source"], context_data)
            except (
                django.template.exceptions.TemplateSyntaxError,
                django.template.exceptions.TemplateDoesNotExist,
            ) as e:
                request.accepted_renderer = JSONRenderer()
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"detail": e.__str__()},
                    content_type="application/json",
                )
            return Response(
                status=status.HTTP_200_OK, data=text, content_type="text/plain"
            )
