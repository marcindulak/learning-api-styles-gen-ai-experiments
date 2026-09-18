from django.conf import settings
from django.core.management.base import BaseCommand

from weather.services import seed_admin_user


class Command(BaseCommand):
    help = "Seeds a single admin user (ADMIN_USERNAME/ADMIN_PASSWORD), once."

    def handle(self, *args, **options):
        seed_admin_user(settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD)
