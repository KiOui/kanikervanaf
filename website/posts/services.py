from django.template.loader import get_template
from django.conf import settings
from smtplib import SMTPException
from django.core.mail import EmailMultiAlternatives
import posts.models as models
from django.contrib.sites.models import Site


def send_post_status_update_email(post):
    """
    Send a post update email message.

    :param post: the post object that has been updated
    :return: True if the mail was sent successfully, False otherwise
    """
    template = get_template("email/post_updated.html")
    template_text = get_template("email/post_updated.txt")

    context = {
        "name": post.author.first_name
        if post.author.first_name is not None and post.author.first_name != ""
        else post.author.username
        if post.author.first_name is not None or post.author.first_name != ""
        else post.author.username,
        "message_title": post.title,
        "status": models.STATUS[post.status][1],
        "domain": Site.objects.get_current().domain,
    }

    text_content = template_text.render(context)
    html_content = template.render(context)

    msg = EmailMultiAlternatives(
        "Kanikervanaf: Bericht status gewijzigd",
        text_content,
        settings.EMAIL_HOST_USER,
        [post.author.email],
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except SMTPException:
        return False

    return True
