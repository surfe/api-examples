import requests
import hmac
import hashlib
from app.config import INTERCOM_ACCESS_TOKEN

class IntercomService:
    def __init__(self):
        self.base_url = "https://api.intercom.io"
        self.headers = {
            "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "2.12"
        }
    
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
    
    def update_conversation_priority(self, conversation_id: str, priority: str = "priority"):
        """
        Update conversation priority
        Args:
            conversation_id: The ID of the conversation to update
            priority: Either "priority" or "not_priority"
        """
        endpoint = f"{self.base_url}/conversations/{conversation_id}"
        
        payload = {
            "priority": priority
        }
        
        try:
            response = requests.put(
                endpoint,
                headers=self.headers,
                json=payload
            )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error updating conversation priority: {str(e)}")
            raise Exception(f"Failed to update conversation priority: {str(e)}")