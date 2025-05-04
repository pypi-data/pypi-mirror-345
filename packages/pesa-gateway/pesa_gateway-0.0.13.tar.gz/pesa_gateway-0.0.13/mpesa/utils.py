import hashlib
import hmac
import requests
from typing import Dict, Any
from mpesa.exceptions import MpesaAPIError


class Utility:
    @classmethod
    def make_request(cls, method: str, url: str, **kwargs):
        response = requests.request(
            method=method, url=url, **kwargs, timeout=kwargs.get("timeout", 30)
        )
        try:
            # response.raise_for_status()
            return {"status_code": response.status_code, "response": response.json()}
        except requests.exceptions.JSONDecodeError:
            raise MpesaAPIError("Invalid JSON response")
        except requests.exceptions.ReadTimeout:
            raise MpesaAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise MpesaAPIError("Failed to connect to the server")
        except requests.exceptions.HTTPError as e:
            raise MpesaAPIError(f"HTTP error: {e}")
        except Exception as e:
            raise MpesaAPIError(f"Request failed: {str(e)}")

    @classmethod
    def encrypt_string(cls, string: str, key: str) -> str:
        """
        Encrypt a string using SHA256 and the MPESA key.

        Args:
            string (str): The string to encrypt
            key (str): The encryption key

        Returns:
            str: The encrypted string
        """
        # Create HMAC SHA256 hash using the key
        hmac_obj = hmac.new(key.encode("utf-8"), string.encode("utf-8"), hashlib.sha256)

        # Get the hex digest
        encrypted = hmac_obj.hexdigest()

        return encrypted
