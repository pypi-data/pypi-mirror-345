"""Example module to demonstrate package structure.

This module can be used as a starting point for development.
"""


def hello(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


class Example:
    """An example class to demonstrate class structure.

    This class serves as a template for creating your own classes.
    """

    def __init__(self, value: str = "default"):
        """Initialize the Example class.

        Args:
            value: An example value. Defaults to "default".
        """
        self.value = value

    def get_value(self) -> str:
        """Get the stored value.

        Returns:
            The stored value.
        """
        return self.value

    def set_value(self, value: str) -> None:
        """Set the stored value.

        Args:
            value: The new value to store.
        """
        self.value = value
