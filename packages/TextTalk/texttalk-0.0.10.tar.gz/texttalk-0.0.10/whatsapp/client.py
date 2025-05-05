from typing import Optional

import requests

from .config import WhatsappConfig
from .exceptions import WhatsAppException


class WhatsAppClient:
    """
    A client for sending WhatsApp messages.
    """

    def __init__(self, config: Optional[WhatsappConfig] = None):
        """
        Initialize the WhatsApp client with configuration.

        Args:
            config (Optional[WhatsappConfig]): Configuration object containing WhatsApp API credentials.
        """
        self.config = config or WhatsappConfig()

    def send_tempate_message(self, data: list[dict]) -> dict:
        """
        Send a template message via WhatsApp API.

        Args:
            data (list[dict]): List of message data dictionaries containing template details

        Returns:
            dict: API response data on success

        Raises:
            WhatsAppException: If the API request fails or returns an error
        """
        if not data:
            raise WhatsAppException("Message data cannot be empty")

        payload = {"messages": data}

        try:
            response = requests.post(
                url=f"{self.config.api_url}/whatsapp/1/message/template",
                headers=self.config.headers,
                json=payload,
                timeout=30,  # Add timeout
            )

            response_data = response.json()

            if response.status_code != 200:
                error_msg = response_data.get("error", {}).get("message", response.text)
                raise WhatsAppException(
                    f"Failed to send WhatsApp message. Status code: {response.status_code}. "
                    f"Error: {error_msg}"
                )

            return response_data

        except requests.Timeout:
            raise WhatsAppException("Request timed out while sending WhatsApp message")

        except requests.RequestException as e:
            raise WhatsAppException(
                f"Request failed while sending WhatsApp message: {str(e)}"
            )

        except Exception as e:
            raise WhatsAppException(
                f"Unexpected error while sending WhatsApp message: {str(e)}"
            )
