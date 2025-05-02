"""
Tests for rey.
"""

import pytest


def test_version():
    """Test that the package has a version."""
    try:
        from rey._version import __version__

        assert isinstance(__version__, str)
    except ImportError:
        pytest.fail("Version module not found")
