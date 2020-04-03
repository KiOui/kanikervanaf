from .models import QueuedMailList, Subscription
from users.models import UserInformation
import logging

logger = logging.getLogger(__name__)


def store_subscription_list(subscription_list):
    """
    Create a set with all ids corresponding to subscription items in subscription_list.

    :param subscription_list: a list of items containing ids corresponding to the subscription objects to add to the
    returned set
    :return: a set with all subscriptions having a corresponding id in the items in subscription_list
    """
    subscription_objects = set()
    for item in subscription_list:
        if "id" in item:
            if Subscription.objects.filter(id=item["id"]).exists():
                subscription_objects.add(Subscription.objects.get(id=item["id"]))
    return subscription_objects


def handle_verification_request(user_information, subscription_list):
    """
    Handle a verification request, generate a QueuedMailList.

    :param user_information: the user information to add to the QueuedMailList
    :param subscription_list: the list of items with ids corresponding to subscription objects
    :return: True if a QueuedMailList was generated, False otherwise
    """
    subscription_objects = store_subscription_list(subscription_list)
    if "email" in user_information and "first_name" in user_information:
        user_information_object = UserInformation.objects.create(
            firstname=user_information.get("first_name"),
            lastname=user_information.get("second_name", ""),
            address=user_information.get("address", ""),
            postal_code=user_information.get("postal_code", ""),
            residence=user_information.get("residence", ""),
            email_address=user_information.get("email"),
        )
        try:
            return QueuedMailList.generate(
                user_information_object, subscription_objects
            )
        except Exception as e:
            logger.error(e)
            user_information_object.delete()
            return False
    else:
        return False
