"""Step definitions for user management features."""

from behave import given
from django.contrib.auth import get_user_model


@given('a regular user "{username}" with password "{password}" exists')
def step_create_regular_user(context, username: str, password: str) -> None:
    """Create a regular user in the database."""
    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username, f'{username}@example.com', password)
