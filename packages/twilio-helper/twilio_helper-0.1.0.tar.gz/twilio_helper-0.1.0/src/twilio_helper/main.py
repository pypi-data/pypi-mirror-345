from typing import Optional, Dict

from twilio.base.exceptions import TwilioRestException, TwilioException
from twilio.rest import Client


class TwilioHelper:
    """
    A helper class to validate Twilio credentials and send WhatsApp messages.
    """

    def __init__(self,
                 account_sid: str,
                 auth_token: str):
        """
       Initializes the TwilioHelper instance and validates credentials.

       Raises:
           ValueError: If credentials are invalid.
       """
        self.account_sid = account_sid.strip()
        self.auth_token = auth_token.strip()

        if not self.account_sid or not self.auth_token:
            raise ValueError("Account SID and Auth Token must not be empty.")

        if not self.validate_twilio_credentials():
            raise ValueError(
                f"Invalid Twilio credentials.\n"
                f"Account SID: {self.account_sid}"
            )

    def validate_twilio_credentials(self) -> bool:
        """
        Validates the provided Twilio Account SID and Auth Token.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        try:
            client = Client(self.account_sid, self.auth_token)
            client.api.accounts(self.account_sid).fetch()
            return True
        except TwilioRestException:
            return False
        except TwilioException:
            return False
        except Exception:
            return False

    def send_whatsapp_message(self,
                              message: str,
                              from_number: str,
                              to_number: str) -> Optional[Dict[str, str]]:
        """
        Sends a WhatsApp message using Twilio.

        Args:
            message (str): The message to send.
            from_number (str): The Twilio WhatsApp sender number (e.g. 'whatsapp:+14155238886').
            to_number (str): The recipient's WhatsApp number (e.g. 'whatsapp:+919999999999').

        Returns:
            dict: Dictionary with message SID if sent successfully.
            None: If the message fails to send.
        """
        try:
            if not all([message.strip(), from_number.strip(), to_number.strip()]):
                raise ValueError("Message, from_number, and to_number cannot be empty.")

            client = Client(self.account_sid, self.auth_token)
            msg = client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            return {"message_sid": msg.sid}
        except Exception:
            return None
