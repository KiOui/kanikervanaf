from smtplib import SMTPException
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
import logging
from django.template.loader import get_template

logger = logging.getLogger(__name__)


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
        "domain": Site.objects.get_current().domain,
    }

    html_content = template.render(context)
    text_content = template_text.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: Contactformulier",
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
