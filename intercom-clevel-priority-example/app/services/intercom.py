import requests
import hmac
import hashlib
from app.config import INTERCOM_ACCESS_TOKEN



class IntercomService:
    def __init__(self):
        self.base_url = "https://api.intercom.io"
        self.headers = {
            "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "Intercom-Version": "2.1"
        }
        self.c_level_tag_id = "10853140"
    
    def verify_webhook_signature(self, secret: str, signature: str, message: bytes) -> bool:
        """
        Verify the Intercom webhook signature.
        
        Args:
            secret: The webhook secret key
            signature: The signature from the X-Hub-Signature header
            message: The raw request body bytes
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        expected_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=message,
            digestmod=hashlib.sha1
        ).hexdigest()
        
        return hmac.compare_digest(f"sha1={expected_signature}", signature)
            
    def get_contact_details(self, contact_id: str):
        """
        Get contact details
        """
        endpoint = f"{self.base_url}/contacts/{contact_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()
    
    def add_conversation_tag(self, conversation_id: str, admin_id: str):
        """
        Add a tag to a conversation
        """
        try:
            endpoint = f"{self.base_url}/conversations/{conversation_id}/tags"
            payload = {
                "id": self.c_level_tag_id,
                "admin_id": admin_id
            }
            response = requests.post(endpoint, json=payload, headers=self.headers)
            if response.json().get("id") != self.c_level_tag_id:
                raise Exception("Failed to add conversation tag")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error adding conversation tag: {str(e)}")
            raise Exception(f"Failed to add conversation tag: {str(e)}")
