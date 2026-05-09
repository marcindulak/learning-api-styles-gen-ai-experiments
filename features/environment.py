"""Behave environment hooks shared by all feature suites."""

from __future__ import annotations

import pathlib


def before_all(context) -> None:
    """Expose the absolute path of the project root to every step."""

    # features/environment.py -> features/ -> project root
    context.project_root = pathlib.Path(__file__).resolve().parent.parent
