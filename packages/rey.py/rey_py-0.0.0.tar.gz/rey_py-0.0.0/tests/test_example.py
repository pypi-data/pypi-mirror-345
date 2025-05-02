"""
Tests for the example module.
"""

from rey.example import Example, hello


def test_hello():
    """Test the hello function."""
    # Test with default parameter
    assert hello() == "Hello, World!"

    # Test with custom parameter
    assert hello("Test") == "Hello, Test!"


class TestExample:
    """Test suite for the Example class."""

    def test_init(self):
        """Test the initialization of Example class."""
        # Test with default parameter
        example = Example()
        assert example.value == "default"

        # Test with custom parameter
        example = Example("custom")
        assert example.value == "custom"

    def test_get_value(self):
        """Test the get_value method."""
        example = Example("test_value")
        assert example.get_value() == "test_value"

    def test_set_value(self):
        """Test the set_value method."""
        example = Example()
        example.set_value("new_value")
        assert example.value == "new_value"
        assert example.get_value() == "new_value"
