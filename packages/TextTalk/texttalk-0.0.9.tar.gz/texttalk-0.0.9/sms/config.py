import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SMSConfig:
    """
    Configuration class for the SMS client.
    
    This class handles configuration settings needed to interact with an SMS API service.
    It manages API credentials and endpoint information, which can be provided directly
    or loaded from environment variables.
    
    Attributes:
        api_key (str): The API key for authentication
        partner_id (str): Partner ID for the SMS service
        shortcode (str): Shortcode used for sending messages
        headers (dict): HTTP headers used in API requests
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        partner_id: Optional[str] = None,
        shortcode: Optional[str] = None,
    ):
        """
        Initialize SMS configuration with API credentials and settings.
        
        The configuration values can be provided directly as arguments or will be loaded
        from environment variables if not specified.
        
        Args:
            api_key (Optional[str]): API key for authentication. If None, loads from SMS_API_KEY env var
            partner_id (Optional[str]): Partner ID for the service. If None, loads from SMS_PARTNER_ID env var
            shortcode (Optional[str]): Shortcode for sending messages. If None, loads from SMS_SHORTCODE env var
            
        Raises:
            ValueError: If any required configuration values are missing from both arguments
                       and environment variables
        """
        self.api_key = api_key or os.getenv('SMS_API_KEY')
        self.partner_id = partner_id or os.getenv('SMS_PARTNER_ID')
        self.shortcode = shortcode or os.getenv('SMS_SHORTCODE')
        self.api_url = "https://sms.textsms.co.ke/api"
        
        if not self.api_key or not self.partner_id or not self.shortcode:
            raise ValueError(
                "Missing required configuration. Please provide credentials either "
                "directly or through environment variables: SMS_API_KEY, SMS_PARTNER_ID, SMS_SHORTCODE"
            ) 
        
        self.headers = {
            "Content-Type": "application/json",
        }