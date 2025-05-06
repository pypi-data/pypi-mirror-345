import requests
from email.mime.base import MIMEBase
import re
from pathlib import Path
from .exeptions import MailTransportAPIError
DEFAULT_ATTACHMENT_MIME_TYPE = "application/octet-stream"

class IdentityClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.mailtransportai.com/api/v1/transport"
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
    def create(self, domain_name: str) -> dict:
        """
        Create a new identity.
        """
    
        url = f"{self.base_url}/identity"
        data = {
            "name": domain_name,
        }
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        try:
            if response.status_code != 201:
                raise MailTransportAPIError(response.json(), response.status_code)
            
            return response.json()
        except (requests.exceptions.RequestException, Exception) as e:
            raise MailTransportAPIError({"error": str(e)}, 500)

    def delete(self, identity_id):
        """
        Delete an identity.
        """
        
        url = f"{self.base_url}/identity/{identity_id}"
        response = requests.delete(url, headers=self.get_headers())
        try:
            if not response.ok:
                raise MailTransportAPIError(response.json(), response.status_code)
            return {"message": "Identity deleted successfully"}
        except (requests.exceptions.RequestException, Exception) as e:
            raise MailTransportAPIError({"error": str(e)}, 500)

    def update(self, identity_id, domain_name):
        """
        Update an identity.
        """
        
        url = f"{self.base_url}/identity/{identity_id}"
        data = {
            "name": domain_name,
        }
        
        response = requests.put(url, headers=self.get_headers(), json=data)
        try:
            if not response.ok:
                raise MailTransportAPIError(response.json(), response.status_code)
            return response.json()
        except (requests.exceptions.RequestException, Exception) as e:
            raise MailTransportAPIError({"error": str(e)}, 500)

    def get(self, identity_id):
        """
        Get an identity.
        """ 
        url = f"{self.base_url}/identity/{identity_id}"
        try:
            response = requests.get(url, headers=self.get_headers())
            if not response.ok:
                raise MailTransportAPIError(response.json(), response.status_code)
            return response.json()
        except (requests.exceptions.RequestException, Exception) as e:
            raise MailTransportAPIError({"error": str(e)}, 500)

    def list(self):
        """
        Get all identities.
        """ 
        url = f"{self.base_url}/identity"
        print(url, '>>>>>>>>>>>>>')
        response = requests.get(url, headers=self.get_headers())
        try:
            if not response.ok:
                raise MailTransportAPIError(response.text, response.status_code)
            return response.json()
        except (requests.exceptions.RequestException, Exception) as e:
            print(str(e))
            raise MailTransportAPIError({"error": str(e)}, 400)

    def verify(self, identity_id):
        """
        Verify an identity.
        """ 
        url = f"{self.base_url}/identity/{identity_id}"
        response = requests.post(url, headers=self.get_headers())
        try:
            if not response.ok:
                raise MailTransportAPIError(response.json(), response.status_code)
            return response.json()
        except (requests.exceptions.RequestException, Exception) as e:
            raise MailTransportAPIError({"error": str(e)}, 500)
