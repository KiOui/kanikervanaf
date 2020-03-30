from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from smtplib import SMTPException
from subscriptions.models import QueuedMailList
from pdfgenerator.services import render_deregister_letter
import logging

logger = logging.getLogger(__name__)


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

    context = {"verification_url": verification_url, "firstname": first_name}

    text_content = template_text.render(context)
    html_content = template.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: verificatie",
        text_content,
        settings.EMAIL_HOST_USER,
        [email_address],
    )
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
        logger.info("Send completed")
    except SMTPException as e:
        logger.error(e)
        return False

    return True


def send_summary_email(
    succeeded_mails,
    failed_mails,
    succeeded_letters,
    failed_letters,
    pdfs,
    user_information,
    direct_send=False,
):
    """
    Send a summary email.
    
    :param succeeded_mails: the list with subscriptions that succeeded sending a deregister email
    :param failed_mails: the list with subscriptions that failed sending a deregister email
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
        msg.attach(None, pdf, "application/pdf")

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
    and created pdfs
    """
    succeeded = list()
    failed = list()
    pdfs = list()
    for item in mail_list.item_list.iterator():
        if item.can_generate_pdf():
            pdfs.append(render_deregister_letter(mail_list.user_information, item))
            succeeded.append(item)
        else:
            failed.append(item)

    return succeeded, failed, pdfs


def handle_deregister_request(mail_list):
    """
    Handle a deregister request.

    :param mail_list: the request to handle
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


def send_deregister_emails(mail_list, direct_send=False):
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
                subscription.name,
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


def create_deregister_email(user_information, subscription, forward_address=False):
    """
    Create a deregister email.

    :param user_information: the user information to put in the deregister email
    :param subscription: the subscription name to put in the deregister email
    :param forward_address: a forwarding address, if this mail is not send directly. This address is noted at the top
    of the created email
    :return: the deregister email with filled in user information
    """
    template = get_template("email/deregister_mail.txt")

    context = {
        "firstname": user_information.firstname,
        "lastname": user_information.lastname,
        "address": user_information.address,
        "postalcode": user_information.postal_code,
        "residence": user_information.residence,
        "subscription": subscription,
        "forward_address": forward_address,
    }

    return template.render(context)


def send_contact_email(name, email_address, title, message):
    """
    Construct and send a contact email.

    :param name: the name of the person sending the contact email
    :param email_address: the email-address of the person sending the contact email
    :param title: the title of the contact email
    :param message: the message of the contact email
    :return: True if the sending succeeded, False otherwise
    """
    template = get_template("email/contact_mail.html")
    template_text = get_template("email/contact_mail.txt")

    context = {
        "name": name,
        "email": email_address,
        "title": title,
        "message": message,
    }

    html_content = template.render(context)
    text_content = template_text.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: Contactformulier",
        text_content,
        settings.EMAIL_HOST_USER,
        ["klantenservice@kanikervanaf.nl"],
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
    }

    html_content = template.render(context)
    text_content = template_text.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: Abonnement aangevraagd",
        text_content,
        settings.EMAIL_HOST_USER,
        ["klantenservice@kanikervanaf.nl"],
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
