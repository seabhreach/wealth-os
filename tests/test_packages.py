"""Package-level smoke tests."""

import dashboard
import engine


def test_top_level_packages_import() -> None:
    """The distributable top-level packages can be imported."""
    assert dashboard.__name__ == "dashboard"
    assert engine.__name__ == "engine"
