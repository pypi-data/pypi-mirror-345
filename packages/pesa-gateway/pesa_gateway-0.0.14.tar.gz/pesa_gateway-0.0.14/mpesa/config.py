import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MpesaConfig:
    """
    Configuration class for M-Pesa API integration.

    This class handles configuration settings for connecting to the M-Pesa API,
    including authentication credentials and environment settings.

    Args:
        consumer_key (Optional[str]): The consumer key for API authentication.
            Defaults to MPESA_CONSUMER_KEY environment variable if not provided.
        consumer_secret (Optional[str]): The consumer secret for API authentication.
            Defaults to MPESA_CONSUMER_SECRET environment variable if not provided.
        shortcode (Optional[str]): The M-Pesa shortcode for the business.
            Defaults to MPESA_SHORTCODE environment variable if not provided.
        passkey (Optional[str]): The passkey for generating security credentials.
            Defaults to MPESA_PASSKEY environment variable if not provided.
        callback_url (Optional[str]): URL where M-Pesa will send transaction notifications.
            Defaults to MPESA_CALLBACK_URL environment variable if not provided.
        environment (Optional[str]): API environment to use - either "sandbox" or "production".
            Defaults to "sandbox".

    Attributes:
        consumer_key (str): The consumer key used for API authentication
        consumer_secret (str): The consumer secret used for API authentication
        shortcode (str): The business shortcode
        passkey (str): The passkey for security credentials
        callback_url (str): The notification callback URL
        environment (str): The API environment being used
        production_url (str): The production API base URL
        sandbox_url (str): The sandbox API base URL
        base_url (str): The active API base URL based on environment
    """

    def __init__(
        self,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        shortcode: Optional[str] = None,
        passkey: Optional[str] = None,
        callback_url: Optional[str] = None,
        environment: Optional[str] = "sandbox",
    ):

        self.consumer_key = consumer_key or os.getenv("MPESA_CONSUMER_KEY")
        self.consumer_secret = consumer_secret or os.getenv("MPESA_CONSUMER_SECRET")
        self.shortcode = shortcode or os.getenv("MPESA_SHORTCODE")
        self.passkey = passkey or os.getenv("MPESA_PASSKEY")
        self.callback_url = callback_url or os.getenv("MPESA_CALLBACK_URL")
        self.environment = os.getenv("MPESA_ENVIRONMENT") or environment
        self.production_url = "https://api.safaricom.co.ke"
        self.sandbox_url = "https://sandbox.safaricom.co.ke"
        self.base_url = (
            self.production_url
            if self.environment == "production"
            else self.sandbox_url
        )
