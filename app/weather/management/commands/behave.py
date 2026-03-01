"""Behave management command for Django."""
import os
import sys

from behave.__main__ import main as behave_main
from django.core.management.base import BaseCommand
from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment, teardown_test_environment


class Command(BaseCommand):
    """Run behave tests with Django test environment."""

    help = 'Run behave BDD tests'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Run tests without prompts',
        )
        parser.add_argument(
            'args',
            nargs='*',
            help='Additional behave arguments',
        )

    def handle(self, *args, **options):
        """Execute behave tests."""
        setup_test_environment()
        test_runner = DiscoverRunner(interactive=not options.get('no_input', False))
        old_db_config = test_runner.setup_databases()

        try:
            behave_args = list(options.get('args', []))

            features_dir = os.path.join(os.getcwd(), 'features')
            if os.path.exists(features_dir):
                behave_args.insert(0, features_dir)

            sys.argv = ['behave'] + behave_args
            exit_code = behave_main()

            if exit_code != 0:
                sys.exit(exit_code)
        finally:
            test_runner.teardown_databases(old_db_config)
            teardown_test_environment()
