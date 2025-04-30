"""
Surfe API Core Service
"""
import time
import requests


class SurfeService:
    """Service for interacting with the Surfe API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.surfe.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def prepare_people_payload(self, people_data, enrichment_type="emailAndMobile", list_name=None):
        """
        Prepare people data for Surfe enrichment API
        
        Args:
            people_data: List of people to enrich
            enrichment_type: Type of enrichment to perform
            list_name: Name of the list for tracking
            
        Returns:
            Prepared payload for Surfe API
        """
        if not list_name:
            list_name = f"Enrichment {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
        return {
            "enrichmentType": enrichment_type,
            "listName": list_name,
            "people": people_data
        }
    
    def start_enrichment(self, payload):
        """
        Start the bulk enrichment process with Surfe API
        
        Args:
            payload: Prepared payload with people data
            
        Returns:
            Enrichment ID
        """
        url = f"{self.base_url}/people/enrichments/bulk"
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["id"]
    
    def poll_enrichment_status(self, enrichment_id, max_attempts=60, delay=5):
        """
        Poll the enrichment status until it's complete
        
        Args:
            enrichment_id: ID of the enrichment process
            max_attempts: Maximum number of polling attempts
            delay: Delay between polling attempts in seconds
            
        Returns:
            Enrichment results
        """
        url = f"{self.base_url}/people/enrichments/bulk/{enrichment_id}"
        
        attempts = 0
        while attempts < max_attempts:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            if status == "COMPLETED":
                return data
            elif status == "FAILED":
                raise Exception(f"Enrichment failed: {data.get('error', 'Unknown error')}")
            
            print(f"Enrichment status: {status}. Waiting {delay} seconds...")
            time.sleep(delay)
            attempts += 1
        
        raise Exception("Enrichment timed out")