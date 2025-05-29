"""
Surfe API Core Service
"""
import time
import requests


class SurfeService:
    """Service for interacting with the Surfe API"""
    
    def __init__(self, api_key, version="v1"):
        self.version = version
        self.api_key = api_key
        self.base_url = f"https://api.surfe.com/{version}"
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
        
        json = {}
        if self.version == "v2":
            json = {
                "include": {
                    "email": True,
                    "mobile": True
                },
                "people": people_data
            }
        else:
            json = {
                "enrichmentType": enrichment_type,
                "listName": list_name,
                "people": people_data,
                "include": {
                    "email": True,
                    "mobile": True
                }
            }
        return json
       
    
    def start_enrichment(self, payload):
        """
        Start the bulk enrichment process with Surfe API
        
        Args:
            payload: Prepared payload with people data
            
        Returns:
            Enrichment ID
        """
        if self.version == "v2":
            url = f"{self.base_url}/people/enrich"
        else:
            url = f"{self.base_url}/people/enrichments/bulk"

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if self.version == "v2":
            return data["enrichmentID"]
        else:
            return data["id"]
    
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
        if self.version == "v2":
            url = f"{self.base_url}/people/enrich/{enrichment_id}"
        else:
            url = f"{self.base_url}/people/enrichments/bulk/{enrichment_id}"
            
        
        attempts = 0
        while attempts < max_attempts:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            status = data.get("status")
            if status == "COMPLETED":
                return data.get("people",[])
            elif status == "FAILED":
                raise Exception(f"Enrichment failed: {data.get('error', 'Unknown error')}")
            
            print(f"Enrichment status: {status}. Waiting {delay} seconds...")
            time.sleep(delay)
            attempts += 1
        
        raise Exception("Enrichment timed out")

    def search_company_lookalikes(self, company_domains, limit=10):
        """
        Search for companies similar to the provided company domains
        
        Args:
            company_domains: List of company domains to find lookalikes for
            limit: Maximum number of results per page (1-200)
            page_token: Token for pagination
            
        Returns:
            Lookalike company search results
        """
        if self.version != "v1":
            raise Exception("Company lookalikes search is only available in API v1")
        
        url = f"{self.base_url}/organizations/lookalikes"
        
        payload = {
            "domains": company_domains,
            "maxResults": min(max(limit, 1), 10)
        }
        
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def extract_companies_from_deals(self, deals_data):
        """
        Extract unique company domains from deals data
        
        Args:
            deals_data: List of deals from CRM
            
        Returns:
            List of unique company domains
        """
        domains = set()
        
        for deal in deals_data:
            # Try to extract domain from organization data
            if deal.get("org_id") and isinstance(deal["org_id"], dict):
                org_data = deal["org_id"]
                
                # Check if domain is directly available
                if org_data.get("domain"):
                    domains.add(org_data["domain"])
                
                # Extract domain from company website/URL
                elif org_data.get("website"):
                    website = org_data["website"]
                    # Clean up the URL to extract domain
                    if website.startswith(("http://", "https://")):
                        domain = website.split("//")[1].split("/")[0]
                    else:
                        domain = website.split("/")[0]
                    domains.add(domain)
            
            # Try to extract from person email if available
            if deal.get("person_id") and isinstance(deal["person_id"], dict):
                person_data = deal["person_id"]
                emails = person_data.get("email", [])
                
                if isinstance(emails, list):
                    for email_obj in emails:
                        if isinstance(email_obj, dict) and email_obj.get("value"):
                            email = email_obj["value"]
                        else:
                            email = str(email_obj)
                        
                        if "@" in email:
                            domain = email.split("@")[1]
                            # Skip common email providers
                            if domain not in ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]:
                                domains.add(domain)
        
        return list(domains)
