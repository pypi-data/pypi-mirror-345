import phonenumbers 
from .exceptions import PhoneNumberError


class PhoneNumberValidator:
    """
    Validator for phone numbers that ensures they are valid and formats them to E.164 format.
    
    Args:
        instance: Optional instance to validate against
        
    Raises:
        ValidationError: If the phone number is invalid or cannot be formatted
        
    Returns:
        str: The phone number formatted in E.164 format
    """
    def __init__(self, instance=None):
        self.instance = instance

    def __call__(self, phone_number):
        """
        Validate and format a phone number.
        
        Args:
            phone_number (str): The phone number to validate and format
            
        Raises:
            ValidationError: If the phone number is invalid or cannot be formatted
            
        Returns:
            str: The phone number formatted in E.164 format
        """
        if phone_number.startswith("0"):
            phone_number = "+254" + phone_number[1:]
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
        except phonenumbers.NumberParseException:
            raise PhoneNumberError("Invalid phone number")

        try:
            formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberFormatingException:
            raise PhoneNumberError("Invalid phone number")

        return formatted_number
    