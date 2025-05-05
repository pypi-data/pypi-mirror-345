import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class WhatsappConfig:
    """
    Configuration class for the Whatsapp client.

    This class handles configuration settings needed to interact with a Whatsapp API service.
    It manages API credentials and endpoint information, which can be provided directly
    or loaded from environment variables.

    Attributes:
        api_key (str): The API key for authentication with the Whatsapp API
        sender (str): The sender ID/phone number for sending Whatsapp messages
        api_url (str): The base URL for the Whatsapp API endpoints
        headers (dict): HTTP headers used in API requests, including auth and content-type
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        sender: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("WHATSAPP_API_KEY")
        self.sender = sender or os.getenv("WHATSAPP_SENDER")
        self.api_url = api_url or os.getenv("WHATSAPP_API_URL")

        if not self.api_key or not self.sender or not self.api_url:
            raise ValueError(
                "Missing required configuration. Please provide credentials either "
                "directly or through environment variables: WHATSAPP_API_KEY, WHATSAPP_SENDER, WHATSAPP_API_URL"
            )

        self.headers = {
            "Authorization": f"App {self.api_key}",
            "Content-Type": "application/json",
        }
