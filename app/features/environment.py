from django.test import Client


def before_scenario(context, scenario):
    context.client = Client()
