import requests
from typing import List, Optional
from .exceptions import SMSException
from .config import SMSConfig


class Message:
    """
    Represents an SMS message.
    """

    def __init__(self, to_number: str, message: str, clientsmsid: str):
        """
        Initialize a new SMS message.

        Args:
            to_number (str): The recipient's phone number (E.164 format)
            message (str): The message content
            clientsmsid (str): The client's SMS ID
        """
        self.to_number = to_number
        self.message = message
        self.clientsmsid = clientsmsid

    def __str__(self) -> str:
        """
        Returns a string representation of the message.

        Returns:
            str: A string representation of the message
        """
        return f"Message to {self.to_number}: {self.message}"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the message.

        Returns:
            str: A detailed string representation of the message
        """
        return f"Message(to_number='{self.to_number}', message='{self.message}', clientsmsid='{self.clientsmsid}')"


class SMSClient:
    """
    A client for sending SMS messages.
    """

    def __init__(self, config: Optional[SMSConfig] = None):
        """
        Initialize the SMS client with configuration.

        Args:
            config (Optional[SMSConfig]): Configuration object containing Twilio credentials.
                                        If None, will try to load from environment variables.
        """
        self.config = config or SMSConfig()

    def send_sms(
        self,
        to_number: str,
        message: str,
    ) -> bool:
        """
        Send an SMS message.

        Args:
            to_number (str): The recipient's phone number (E.164 format)
            message (str): The message content
        """

        payload = {
            "apikey": self.config.api_key,
            "partnerID": self.config.partner_id,
            "mobile": str(to_number),
            "message": message,
            "shortcode": self.config.shortcode,
            "pass_type": "plain",
        }

        try:
            response = requests.post(
                url=f"{self.config.api_url}/services/sendsms/",
                headers=self.config.headers,
                json=payload,
                timeout=30,
            )
            print(response.json())
            return response.status_code == 200
        except Exception as e:
            raise SMSException(f"Unexpected error while sending SMS: {str(e)}")

    def send_bulk_sms(self, messages: List[Message]) -> bool:
        """
        Send a bulk SMS message to multiple recipients.

        Args:
            message (str): The message content
            to_numbers (List[str]): List of recipient phone numbers

        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        payload = [
            {
                "apikey": self.config.api_key,
                "partnerID": self.config.partner_id,
                "mobile": str(message.to_number),
                "message": message.message,
                "clientsmsid": message.clientsmsid,
                "shortcode": self.config.shortcode,
                "pass_type": "plain",
            }
            for message in messages
        ]

        data = {"count": len(payload), "smslist": payload}

        try:
            response = requests.post(
                url=f"{self.config.api_url}/services/sendbulk/",
                headers=self.config.headers,
                json=data,
                timeout=30,
            )
            return response.status_code == 200, response.json()
        except Exception as e:
            raise SMSException(f"Unexpected error while sending bulk SMS: {str(e)}")
