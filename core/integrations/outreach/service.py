"""
Outreach API Service Module
"""
import requests
import json
from urllib.parse import urljoin


class OutreachService:
    """Service for interacting with the Outreach API"""
    
    def __init__(self, access_token, api_base_url="https://api.outreach.io/api/v2"):
        self.access_token = access_token
        self.api_base_url = api_base_url
        
    def _make_request(self, method, endpoint, params=None, data=None, json_data=None):
        """
        Make a request to the Outreach API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: URL parameters
            data: Form data
            json_data: JSON data
            
        Returns:
            Response data as dictionary
        """
        url = urljoin(self.api_base_url, endpoint)
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
        }
        
        payload = json.dumps(json_data) if json_data else data
        
        response = requests.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            data=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_mailboxes(self):
        """
        Get a list of mailboxes from Outreach
        
        Returns:
            List of mailboxes
        """
        endpoint = "mailboxes"
        return self._make_request("GET", endpoint)
    
    def get_sequences(self):
        """
        Get a list of sequences from Outreach
        
        Returns:
            List of sequences
        """
        endpoint = "sequences"
        return self._make_request("GET", endpoint)
    
    def create_prospect(self, prospect_data):
        """
        Create a new prospect in Outreach
        
        Args:
            prospect_data: Dictionary containing prospect data
            
        Returns:
            Created prospect data
        """
        endpoint = "prospects"
        
        # Format data for Outreach API (JSON:API format)
        json_data = {
            "data": {
                "type": "prospect",
                "attributes": prospect_data
            }
        }
        
        response = self._make_request("POST", endpoint, json_data=json_data)
        return response
    
    def find_prospect_by_email(self, email):
        """
        Find a prospect by email address
        
        Args:
            email: Email address to search for
            
        Returns:
            Prospect data if found, None otherwise
        """
        endpoint = "prospects"
        params = {
            "filter[emails]": email
        }
        
        response = self._make_request("GET", endpoint, params=params)
        
        if response.get("data") and len(response["data"]) > 0:
            return response["data"][0]
        
        return None
    
    def add_prospect_to_sequence(self, prospect_id, sequence_id, mailbox_id):
        """
        Add a prospect to a sequence
        
        Args:
            prospect_id: ID of the prospect
            sequence_id: ID of the sequence
            mailbox_id: ID of the mailbox to use
            
        Returns:
            Created sequence state data
        """
        endpoint = "sequenceStates"
        
        # Format data for Outreach API (JSON:API format)
        json_data = {
            "data": {
                "type": "sequenceState",
                "relationships": {
                    "prospect": {
                        "data": {
                            "type": "prospect",
                            "id": prospect_id
                        }
                    },
                    "sequence": {
                        "data": {
                            "type": "sequence",
                            "id": sequence_id
                        }
                    },
                    "mailbox": {
                        "data": {
                            "type": "mailbox",
                            "id": mailbox_id
                        }
                    }
                }
            }
        }
        
        response = self._make_request("POST", endpoint, json_data=json_data)
        return response
    
    def format_enriched_data_for_outreach(self, enriched_person, event_name):
        """
        Format enriched data from Surfe for Outreach API
        
        Args:
            enriched_person: Dictionary containing enriched person data
            event_name: Name of the event
            
        Returns:
            Formatted data for Outreach API
        """
        outreach_data = {
            "firstName": enriched_person.get("firstName", ""),
            "lastName": enriched_person.get("lastName", ""),
            "company": enriched_person.get("companyName", ""),
            "title": enriched_person.get("title", ""),
            "occupation": enriched_person.get("jobTitle", ""),
            "linkedinUrl": enriched_person.get("linkedinUrl", ""),
            "websiteUrl1": enriched_person.get("companyDomain", ""),
            "tags": enriched_person.get("department", []) + enriched_person.get("seniorities", []),
            "event": event_name
        }
        
        # Add all valid emails
        if enriched_person.get("emails") and len(enriched_person["emails"]) > 0:
            # Filter for valid emails and extract email addresses
            valid_emails = [
                email.get("email") 
                for email in enriched_person["emails"]
                if email.get("validationStatus") == "VALID" and email.get("email")
            ]
            if valid_emails:
                outreach_data["emails"] = valid_emails
        
        # Add phone if available
        if enriched_person.get("mobilePhones") and len(enriched_person["mobilePhones"]) > 0:
            # Sort by confidence score
            sorted_phones = sorted(
                enriched_person["mobilePhones"],
                key=lambda x: x.get("confidenceScore", 0),
                reverse=True
            )
            if sorted_phones:
                outreach_data["phones"] = [
                    phone.get("mobilePhone") 
                    for phone in sorted_phones 
                    if phone.get("mobilePhone")
                ]
        
        return outreach_data 