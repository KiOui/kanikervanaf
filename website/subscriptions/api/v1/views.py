import datetime
import os
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

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
from subscriptions.api.v1.renderers import PDFRenderer, PlainTextRenderer, WordDocumentRenderer
from subscriptions.api.v1.serializers import (
    SubscriptionSerializer,
    SubscriptionCategorySerializer,
)
from subscriptions.models import Subscription, SubscriptionCategory
from subscriptions.services import (
    render_deregister_letter_pdf,
    render_deregister_letter_docx,
    create_deregister_email,
    render_string,
    render_string_to_pdf,
)
from django.conf import settings


class SubscriptionListAPIView(ListAPIView):
    """
    Subscription List API View.

    Permissions required: None

    Use this endpoint to get a list of subscriptions in the database.
    """

    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'subscriptionsearchterm__name']
    ordering_fields = ['name', 'amount_used']


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
    """Subscription Render Letter API View."""

    schema = CustomAutoSchema(
        request_schema={
            "type": "object",
            "properties": {
                "context": {"type": "object", "example": {x: "string" for x in settings.DEFAULT_TEMPLATE_PARAMETERS}},
            },
        }
    )

    renderer_classes = [WordDocumentRenderer, PDFRenderer]

    def post(self, request, **kwargs):
        """
        Render a letter to PDF or Word document.

        Permission required: None

        A context dictionary may be provided that includes context variables that can be passed to the template.
        """
        try:
            subscription = Subscription.objects.get(pk=kwargs.get("pk"))
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        context = {}
        context.update(settings.DEFAULT_TEMPLATE_PARAMETERS)
        context.update(request.data.get("context", {}))
        if request.accepted_renderer.format == "pdf":
            pdf = render_deregister_letter_pdf(context, subscription)
            return Response(
                status=status.HTTP_200_OK, data=pdf, content_type="application/pdf"
            )
        else:
            docx = render_deregister_letter_docx(context, subscription)
            return Response(
                status=status.HTTP_200_OK, data=docx, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )


class SubscriptionRenderEmailAPIView(APIView):
    """
    Subscription Render Email API View.

    Permission required: None

    Use this endpoint to render the email of a Subscription.
    """

    renderer_classes = [PlainTextRenderer]

    def get(self, request, **kwargs):
        """Get request."""
        try:
            instance = Subscription.objects.get(pk=kwargs.get("pk"))
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if instance.email_template_text:
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
                settings.MEDIA_ROOT, str(instance.email_template_text)
            ),
        )


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

    renderer_classes = [WordDocumentRenderer, PDFRenderer, PlainTextRenderer]
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
