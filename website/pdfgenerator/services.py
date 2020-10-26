from django.template.loader import render_to_string
from weasyprint import HTML


def render_deregister_letter(user_information, item):
    """
    Render a deregister letter.

    :param user_information: the user information
    :param item: the item to render the letter for
    :return:
    """
    item_address, item_postal_code, item_residence = item.get_address_information()
    html = render_to_string(
        "pdf/deregister_letter.html",
        {
            "firstname": user_information.firstname,
            "lastname": user_information.lastname,
            "address": user_information.address,
            "postal_code": user_information.postal_code,
            "residence": user_information.residence,
            "subscription_address": item_address,
            "subscription_postal_code": item_postal_code,
            "subscription_residence": item_residence,
            "subscription_name": item.name,
        },
    )
    pdf = HTML(string=html).write_pdf()
    return pdf
