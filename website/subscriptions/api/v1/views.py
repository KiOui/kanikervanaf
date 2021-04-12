import os

from django.conf import settings
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from subscriptions.api.v1.pagination import StandardResultsSetPagination
from subscriptions.api.v1.serializers import (
    SubscriptionSerializer,
    SubscriptionCategorySerializer,
)
from subscriptions.models import Subscription, SubscriptionCategory
from subscriptions.services import render_deregister_letter
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


class EmailRenderView(APIView):
    """Email Render View."""

    def get(self, request, **kwargs):
        """Render an admin letter."""
        format_obj = kwargs.get("obj")
        slug = kwargs.get("slug")
        if format_obj == "subscription":
            obj = Subscription
        elif format_obj == "subscription-category":
            obj = SubscriptionCategory
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            instance = obj.objects.get(slug=slug)
        except obj.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if instance.letter_template.name:
            pdf = render_deregister_letter(
                UserInformation.get_test_instance(),
                Subscription.get_test_instance(),
                os.path.join(settings.MEDIA_ROOT, str(instance.letter_template)),
            )
            return Response(
                status=status.HTTP_200_OK, data=pdf, content_type="application/pdf"
            )
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
