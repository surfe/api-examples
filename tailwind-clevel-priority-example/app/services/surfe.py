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
    
    async def enrich_contact(self, email: str):
        # TODO: replace with enrichment api using email only
        endpoint = f"{self.base_url}/people/enrichments"

        payload = {
            "enrichmentType": "email",
            "person": {
                "email": email
            }
        }
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
                        
            result = response.json()
        
            while True:
                contact_results_response = requests.get(endpoint, headers=self.headers, json=payload)
                contact_results_data = contact_results_response.json()
                if contact_results_data.get('status') != 'IN_PROGRESS':
                    break
                time.sleep(5)
            return contact_results_data
        except requests.exceptions.RequestException as e:
            print(f"Error enriching contact: {str(e)}")
            raise Exception(f"Failed to enrich contact: {str(e)}")