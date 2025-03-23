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
        
        print(f"Updating conversation priority: {conversation_id} to {priority}")
        query = {
            "display_as": "plaintext"
        }

        payload = {
     
        "priority": priority
         }
        
        try:
            print(f"Payload: {payload}")
            response = requests.put(
                endpoint,
                headers=self.headers,
                json=payload,
                params=query
            )

            data = response.json()
            print(f"Response: {data}")
            
            return {
                "status": "success",
                "conversation_id": conversation_id,
                "priority_updated": data.get("priority")
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error updating conversation priority: {str(e)}")
            raise Exception(f"Failed to update conversation priority: {str(e)}")
        
    def get_contact_details(self, contact_id: str):
        """
        Get contact details
        """
        endpoint = f"{self.base_url}/contacts/{contact_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()
    
    def add_conversation_tag(self, conversation_id: str, admin_id: str, tag: str):
        """
        Add a tag to a conversation
        """
     
        endpoint = f"{self.base_url}/conversations/{conversation_id}/tags"
        payload = {
            "admin_id": admin_id,
            "id": tag
        }
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()