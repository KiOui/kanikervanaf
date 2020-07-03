from smtplib import SMTPException

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from .models import PasswordReset
from django.urls import reverse
from django.conf import settings


def send_new_account(user, password):
    """
    Send a new account notification.

    :param user: the newly created user
    :return: True if the mail was sent successfully, False otherwise
    """
    template_text = get_template("email/new_account.txt")

    context = {"user": user, "password": password}

    text_content = template_text.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: account aangemaakt",
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    try:
        msg.send()
    except SMTPException as e:
        print(e)
        return False
    return True


def send_reset_password(reset, request):
    """
    Send a password reset email.

    :param reset: a PasswordReset object with a linked User object
    :param request: the request
    :return: True if the mail was sent successfully, False otherwise
    """
    template = get_template("email/password_reset.html")
    template_text = get_template("email/password_reset.txt")

    verification_url = request.build_absolute_uri(
        reverse("users:reset", kwargs={"token": reset.token})
    )

    context = {"firstname": reset.user.username, "verification_url": verification_url}

    text_content = template_text.render(context)
    html_content = template.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: wachtwoord reset",
        text_content,
        settings.EMAIL_HOST_USER,
        [reset.user.email],
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except SMTPException as e:
        print(e)
        return False

    return True


def generate_password_reset(user):
    """
    Generate a password reset object.

    :param user: a User object for which to generate the password reset
    :return: the generated PasswordReset object
    """
    reset = PasswordReset.generate(user)
    return reset
