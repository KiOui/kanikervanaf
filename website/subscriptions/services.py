import os

from django.contrib.sites.models import Site
from django.template import Template, Context, Engine
from weasyprint import HTML
from .models import QueuedMailList, Subscription
from users.models import UserInformation
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from smtplib import SMTPException
import logging
import datetime

logger = logging.getLogger(__name__)


def render_string_to_pdf(template: str, context: dict, use_django_engine=False):
    """Render a template with context to pdf."""
    rendered_str = render_string(template, context, use_django_engine=use_django_engine)
    return HTML(string=rendered_str).write_pdf()


def render_string(template: str, context: dict, use_django_engine=False):
    """Render template string with context."""
    if use_django_engine:
        engine = None
    else:
        engine = Engine()

    return Template(template, engine=engine).render(Context(context))


def render_deregister_letter(user_information, item, letter_template=None):
    """
    Render a deregister letter.

    :param letter_template: the letter template to use, if specified this template will be used instead of the one
    registered in the subscription
    :param user_information: the user information
    :param item: the item to render the letter for
    :return:
    """
    item_address, item_postal_code, item_residence = item.get_address_information()
    template = (
        get_file_contents(item.get_letter_template())
        if letter_template is None
        else get_file_contents(letter_template)
    )
    context = {
        "firstname": user_information.firstname,
        "lastname": user_information.lastname,
        "address": user_information.address,
        "postal_code": user_information.postal_code,
        "residence": user_information.residence,
        "subscription_address": item_address,
        "subscription_postal_code": item_postal_code,
        "subscription_residence": item_residence,
        "subscription_name": item.name,
        "date": datetime.datetime.now().strftime("%d-%m-%Y"),
    }
    return render_string_to_pdf(template, context)


def send_verification_email(first_name, email_address, verification_url):
    """
    Send a verification email to a specified email address.

    :param first_name: the first name to be noted on the verification email
    :param email_address: the email address of the user that will receive the verification mail
    :param verification_url: the verification url (including the verification token) to be put in the verification mail
    button
    :return: True if the mail was send successfully, False otherwise
    This function captures SMTPExceptions and logs them to the console.
    """
    template = get_template("email/verification_mail.html")
    template_text = get_template("email/verification_mail.txt")

    context = {
        "verification_url": verification_url,
        "firstname": first_name,
        "domain": Site.objects.get_current().domain,
    }

    text_content = template_text.render(context)
    html_content = template.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: Verificatie",
        text_content,
        settings.EMAIL_HOST_USER,
        [email_address],
    )
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
    except SMTPException as e:
        logger.error(e)
        return False

    return True


def send_summary_email(
    succeeded_mails: set,
    failed_mails: set,
    succeeded_letters,
    failed_letters,
    pdfs: list,
    user_information: UserInformation,
    direct_send: bool = False,
):
    """
    Send a summary email.

    :param succeeded_mails: the list with subscriptions that succeeded sending a deregister email
    :param failed_mails: the list with subscriptions that failed sending a deregister email
    :param succeeded_letters: a list with letters that succeeded generating
    :param failed_letters: a list with letters that failed generating
    :param pdfs: a list of pdf documents generated
    :param user_information: the user information for the summary email
    :param direct_send: whether or not the deregister emails were send directly to the companies
    :return: True if the mail was send successfully, False otherwise
    This function captures SMTPExceptions and logs them to the console.
    """
    template = get_template("email/confirmation_mail.html")
    template_text = get_template("email/confirmation_mail.txt")

    context = {
        "firstname": user_information.firstname,
        "forward": not direct_send,
        "send_emails": succeeded_mails,
        "unsend_emails": failed_mails,
        "send_letters": succeeded_letters,
        "unsend_letters": failed_letters,
        "domain": Site.objects.get_current().domain,
    }

    html_content = template.render(context)
    text_content = template_text.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf.nl: Mails verzonden",
        text_content,
        settings.EMAIL_HOST_USER,
        [user_information.email_address],
    )
    msg.attach_alternative(html_content, "text/html")
    for pdf in pdfs:
        msg.attach(pdf["item"].slug + ".pdf", pdf["pdf"], "application/pdf")

    try:
        msg.send()
    except SMTPException as e:
        logger.error(e)
        return False

    return True


def create_deregister_letters(mail_list):
    """
    Create deregister letters.

    :param mail_list: the mail list to create the letters for
    :return: a tuple with (succeeded_letters, failed_letters, pdfs) with a list of succeeded letters, failed letters
    and created pdfs in dictionary format {item: item, pdf: pdf_source}
    """
    succeeded = list()
    failed = list()
    pdfs = list()
    for item in mail_list.item_list.iterator():
        if item.can_generate_pdf():
            pdfs.append(
                {
                    "item": item,
                    "pdf": render_deregister_letter(mail_list.user_information, item),
                }
            )
            succeeded.append(item)
        else:
            failed.append(item)

    return succeeded, failed, pdfs


def handle_deregister_request(mail_list):
    """
    Handle a deregister request.

    :param mail_list: the mail list to handle
    :return: True if the summary email was send successfully, False otherwise
    """
    succeeded_mails, failed_mails = send_deregister_emails(mail_list)
    succeeded_letters, failed_letters, pdfs = create_deregister_letters(mail_list)
    retvalue = send_summary_email(
        succeeded_mails,
        failed_mails,
        succeeded_letters,
        failed_letters,
        pdfs,
        mail_list.user_information,
    )
    for subscription in mail_list.item_list.iterator():
        subscription.deregistered()
    mail_list.user_information.delete()
    mail_list.delete()
    QueuedMailList.remove_expired()
    return retvalue


def send_deregister_emails(mail_list, direct_send=False) -> (set, set):
    """
    Send all deregister emails for subscriptions in mail_list.

    :param mail_list: a QueuedMailList object including the user information to be noted in the email and a list of
    subscriptions to send deregister emails for
    :param direct_send: whether or not to send the emails directly to the subscription providers or not
    :return: two sets, the first one with all subscriptions that succeeded sending an email, the other with all
    subscriptions that failed sending an email
    """
    succeeded = set()
    failed = set()

    for subscription in mail_list.item_list.iterator():
        if subscription.support_email is not None and subscription.support_email != "":
            deregister_email = create_deregister_email(
                mail_list.user_information,
                subscription,
                forward_address=False if direct_send else subscription.support_email,
            )
            if direct_send:
                msg = EmailMultiAlternatives(
                    "Kanikervanaf: {}".format(subscription.name),
                    deregister_email,
                    settings.EMAIL_HOST_USER,
                    [subscription.support_email],
                    cc=[mail_list.user_information.email_address],
                    reply_to=mail_list.user_information.email_address,
                )
            else:
                msg = EmailMultiAlternatives(
                    "Kanikervanaf: {}".format(subscription.name),
                    deregister_email,
                    settings.EMAIL_HOST_USER,
                    [mail_list.user_information.email_address],
                )
            try:
                msg.send()
                succeeded.add(subscription)
            except SMTPException as e:
                logger.error(e)
                failed.add(subscription)
        else:
            failed.add(subscription)
    return succeeded, failed


def create_deregister_email(
    user_information, item, email_template=None, forward_address=False
):
    """
    Create a deregister email.

    :param email_template: the email template to use, if specified this template will be used instead of the one
    :param user_information: the user information to put in the deregister email
    :param item: the subscription to put in the deregister email
    :param forward_address: a forwarding address, if this mail is not send directly. This address is noted at the top
    of the created email
    :return: the deregister email with filled in user information
    """
    item_address, item_postal_code, item_residence = item.get_address_information()
    template = (
        get_file_contents(item.get_email_template_text())
        if email_template is None
        else get_file_contents(email_template)
    )

    context = {
        "firstname": user_information.firstname,
        "lastname": user_information.lastname,
        "address": user_information.address,
        "postal_code": user_information.postal_code,
        "residence": user_information.residence,
        "subscription_address": item_address,
        "subscription_postal_code": item_postal_code,
        "subscription_residence": item_residence,
        "subscription_name": item.name,
        "date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "forward_address": forward_address,
    }

    return render_string(template, context)


def send_request_email(name, email_address, subscription, message):
    """
    Construct and send a request email.

    :param name: the name of the person sending the contact email
    :param email_address: the email-address of the person sending the contact email
    :param subscription: the subscription that the user requested
    :param message: the message of the contact email
    :return: True if the sending succeeded, False otherwise
    """
    template = get_template("email/request_mail.html")
    template_text = get_template("email/request_mail.txt")

    context = {
        "name": name,
        "email": email_address,
        "subscription": subscription,
        "message": message,
        "domain": Site.objects.get_current().domain,
    }

    html_content = template.render(context)
    text_content = template_text.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: Abonnement aangevraagd",
        text_content,
        settings.EMAIL_HOST_USER,
        [settings.CUSTOMER_SERVICE_EMAIL],
        bcc=[email_address],
        reply_to=[email_address],
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except SMTPException as e:
        logger.error(e)
        return False

    return True


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


def get_file_contents(filename):
    """
    Get the file contents of a file with filename.

    :param filename: the filename of the file to get the contents of
    :return: the contents of the file or 'There was an error rendering the template file' if the contents could not be
    retrieved
    """
    if os.path.exists(str(filename)):
        with open(filename, "r") as file:
            try:
                return file.read()
            except IOError:
                pass
    logging.error("There was an error rendering the file {}".format(filename))
    return "There was an error rendering the template file"
