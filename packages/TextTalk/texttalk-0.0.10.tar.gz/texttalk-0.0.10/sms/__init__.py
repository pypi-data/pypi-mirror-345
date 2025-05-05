"""
Chatify SMS Library

A Python library for sending SMS messages through a REST API service.

This package provides a simple interface for sending both individual and bulk SMS messages.
It handles configuration management, API authentication, and error handling.

Classes:
    SMSClient: Main client for sending SMS messages
    SMSConfig: Configuration class for API credentials and settings
    SMSException: Base exception class for SMS-related errors
    ConfigurationError: Exception for configuration issues
    MessageError: Exception for message content/format issues
"""

from .client import SMSClient
from .config import SMSConfig
from .exceptions import SMSException, ConfigurationError, MessageError

__version__ = "0.1.0"
__all__ = ["SMSClient", "SMSConfig", "SMSException", "ConfigurationError", "MessageError"]
