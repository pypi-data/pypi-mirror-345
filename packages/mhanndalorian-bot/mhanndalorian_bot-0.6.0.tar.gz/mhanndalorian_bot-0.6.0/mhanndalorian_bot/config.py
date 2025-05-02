"""
Central shared configuration class
"""

from __future__ import annotations, absolute_import

import logging


class Config:
    """
    Provides a configuration template that ensures immutability and prevents instantiation
    or subclassing. It includes functionality to manage and retrieve a debug configuration
    state, ensuring robust control over debugging settings.

    The Config class is designed to act as a utility class, allowing only static interaction
    with its methods and attributes.

    Attributes:
        _debug (bool): Represents the debugging state of the application. Defaults to False.
    """
    _debug: bool = False

    logger = logging.getLogger(__name__)

    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} cannot be instantiated.")

    def __init_subclass__(cls, **kwargs):
        raise TypeError(f"{cls.__name__} cannot be subclassed.")

    @staticmethod
    def get_debug() -> bool:
        """Retrieve the current debug configuration state"""
        return Config._debug

    @staticmethod
    def set_debug(value: bool):
        """Set the debug configuration state"""
        if not isinstance(value, bool):
            raise ValueError("Debug value must be a boolean.")
        Config._debug = value
