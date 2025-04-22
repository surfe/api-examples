"""
Pipedrive API Service Module
"""
import requests
import json


class PipedriveService:
    """Service for interacting with the Pipedrive API"""
    
    def __init__(self, api_key, api_base_url="https://api.pipedrive.com/api/v2"):
        self.api_key = api_key
        self.api_base_url = api_base_url
        
    def _make_request(self, method, endpoint, params=None, data=None, json_data=None):
        """
        Make a request to the Pipedrive API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: URL parameters
            data: Form data
            json_data: JSON data
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.api_base_url}/{endpoint}"
        
        # Ensure api_key is included in all requests
        if params is None:
            params = {}
        params["api_token"] = self.api_key
        
        payload = json.dumps(json_data) if json_data else data if data else None
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        
        response = requests.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            data=payload
        )

        
        response.raise_for_status()
        return response.json()
    
    def get_persons(self, limit=100, include_fields=None, filter_id=None, owner_id=None, org_id=None):
        """
        Get a list of persons from Pipedrive
        
        Args:
            limit: Maximum number of persons to fetch
            include_fields: Fields to include in the response
            filter_id: Filter ID to apply
            owner_id: Owner ID to filter by
            org_id: Organization ID to filter by
            
        Returns:
            List of persons
        """
        params = {
            "limit": limit
        }

        
        # Add optional parameters if provided
        if include_fields:
            params["include_fields"] = include_fields
        if filter_id:
            params["filter_id"] = filter_id
        if owner_id:
            params["owner_id"] = owner_id
        if org_id:
            params["org_id"] = org_id

        response = self._make_request("GET", "persons", params=params)
        
        if not response.get("success"):
            raise Exception(f"Failed to get persons: {response.get('error')}")
        
        return response.get("data", [])
    
    def get_organization_by_id(self, org_id):
        """
        Get an organization by ID from Pipedrive
        
        Args:
            org_id: ID of the organization to fetch
            
        Returns:
            Organization data
        """
        response = self._make_request("GET", f"organizations/{org_id}")
        
        return response.get("data", {})
    
    
    def update_person(self, person_id, update_data):
        """
        Update a person in Pipedrive
        
        Args:
            person_id: ID of the person to update
            update_data: Data to update
            
        Returns:
            Updated person data
        """
        response = self._make_request("PATCH", f"persons/{person_id}", json_data=update_data)
        
        if not response.get("success"):
            raise Exception(f"Failed to update person {person_id}: {response.get('error')}")
        
        return response.get("data", {})
    
    def format_persons_for_surfe(self, persons):
        """
        Format Pipedrive persons for Surfe enrichment
        
        Args:
            persons: List of Pipedrive persons
            
        Returns:
            List of people formatted for Surfe API
        """
        people = []
        
        for person in persons:
            # Extract the data from Pipedrive person object
            person_data = {
                "externalID": str(person["id"]),
                "firstName": person.get("first_name", ""),
                "lastName": person.get("last_name", ""),
            }
            
            # Add company name from organization if available
            if person.get("org_id") and isinstance(person["org_id"], dict):
                person_data["companyName"] = person["org_id"].get("name", "")
            else:
                person_data["companyName"] = self.get_organization_by_id(person["org_id"]).get("name", "")
            
            # TODO: Extract LinkedIn URL from custom fields if available
            
            # TODO: Extract company website from email domain or org data
            email = next((email["value"] for email in person.get("email", []) 
                         if isinstance(email, dict) and email.get("value")), "")
            if email:
                email_domain = email.split("@")[-1] if "@" in email else ""
                if email_domain:
                    person_data["companyWebsite"] = email_domain
            # Only add if we have enough data to enrich
            if ((person_data["firstName"] and person_data["lastName"] and person_data["companyName"]) or
                (person_data["firstName"] and person_data["lastName"] and person_data["companyWebsite"])):
                people.append(person_data)
        
        return people
    
    def prepare_person_update_from_surfe(self, person_id, enriched_data):
        """
        Prepare update data for Pipedrive from Surfe enrichment
        
        Args:
            person_id: Pipedrive person ID
            enriched_data: Enrichment data from Surfe
            
        Returns:
            Update data for Pipedrive API
        """
        # Find the enriched person data by external ID
        enriched_person = None
        for person in enriched_data.get("people", []):
            if person.get("externalID") == str(person_id):
                enriched_person = person
                break
        
        if not enriched_person:
            return None
        
        update_data = {}
        
        # Extract the best email if available
        if enriched_person.get("emails"):
            # Sort by validation status and take the first one
            sorted_emails = sorted(
                enriched_person["emails"], 
                key=lambda x: 0 if x.get("validationStatus") == "VALID" else 1
            )
            if sorted_emails:
                email = sorted_emails[0].get("email")
                if email:
                    update_data["emails"] = [{"value": email, "primary": True}]
        
        # Extract the best mobile phone if available
        if enriched_person.get("mobilePhones"):
            # Sort by confidence score and take the highest
            sorted_phones = sorted(
                enriched_person["mobilePhones"], 
                key=lambda x: x.get("confidenceScore", 0), 
                reverse=True
            )
            if sorted_phones:
                mobile_phone = sorted_phones[0].get("mobilePhone")
                if mobile_phone:
                    update_data["phones"] = [{"value": mobile_phone, "primary": True}]
        
        return update_data if update_data else None
    
