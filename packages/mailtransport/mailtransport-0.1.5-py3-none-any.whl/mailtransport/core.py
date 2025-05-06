from .mail import MailClient
from .identity import IdentityClient


class MailTransportClient(MailClient):
    """
    A client for interacting with the MailTransport API.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.mailtransportai.com/api/v1"
        self.mail_init = False
        self.identity = IdentityClient(
            api_key=api_key
        )