from django.shortcuts import render
from django.views.generic import TemplateView


class BasicUserInformation(TemplateView):

    template_name = "enter_information.html"
