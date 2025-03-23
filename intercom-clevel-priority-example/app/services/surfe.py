import requests
from app.config import SURFE_API_KEY
import time

class SurfeService:
    def __init__(self):
        self.base_url = "https://api.surfe.com/v1"
        self.headers = {
            "Authorization": f"Bearer {SURFE_API_KEY}",
            "Content-Type": "application/json"
        }
    
    async def get_contact_details_by_email(self, email: str):
        endpoint = f"{self.base_url}/people/search/byEmail"

        payload = {
            "email": email,
            "linkedInURLSufficient": False
        }
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=payload
            )
                        
            result = response.json()
            print(f"Result: {result}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error enriching contact: {str(e)}")
            raise Exception(f"Failed to enrich contact: {str(e)}")