"""Seed the database with the 5 biggest cities in the world."""
from django.core.management.base import BaseCommand

from weather.seed import SEEDED_CITIES, seed_cities


class Command(BaseCommand):
    help = "Seed the 5 biggest cities in the world (idempotent)"

    def handle(self, *args, **options):
        created = seed_cities()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(created)} of {len(SEEDED_CITIES)} cities "
                f"({len(SEEDED_CITIES) - len(created)} already present)"
            )
        )
