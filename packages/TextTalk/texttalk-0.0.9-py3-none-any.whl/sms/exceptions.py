class SMSException(Exception):
    """
    Base exception for SMS-related errors.
    """
    pass

class ConfigurationError(SMSException):
    """
    Exception raised when there are issues with SMS configuration.
    """
    pass

class MessageError(SMSException):
    """
    Exception raised when there are issues with the message content or format.
    """
    pass 

class PhoneNumberError(SMSException):
    """
    Exception raised when there are issues with the phone number format.
    """
    pass