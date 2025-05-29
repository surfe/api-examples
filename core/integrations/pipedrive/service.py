"""
Pipedrive API Service Module
"""
from datetime import timezone
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
    
    def find_person_by_email(self, email):
        """
        Find a person by email address
        
        Args:
            email: Email address to search for
            
        Returns:
            Person data if found, None otherwise
        """
        if not email:
            return None
            
        params = {
            "term": email,
            "fields": "email",
            "exact_match": True,
            "limit": 1
        }
        
        response = self._make_request("GET", "persons/search", params=params)
        
        if response.get("success") and response.get("data"):
            items = response["data"].get("items", [])
            if items:
                return items[0]["item"]
        
        return None
    
    def create_person(self, person_data):
        """
        Create a new person in Pipedrive
        
        Args:
            person_data: Person data to create
            
        Returns:
            Created person data
        """
        response = self._make_request("POST", "persons", json_data=person_data)
        
        if not response.get("success"):
            error_details = {
                "error": response.get('error'),
                "error_info": response.get('error_info', {}),
                "status_code": getattr(response, 'status_code', 'unknown'),
                "response": response
            }
            raise Exception(f"Failed to create person: {json.dumps(error_details, indent=2)}")        
        return response.get("data", {})
    
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
    
    def search_organization(self, organization_data):
        """
        Search for an organization in Pipedrive
        """
        response = self._make_request("GET", "organizations/search", params=organization_data)
        return response.get("data", {})
    
    def create_organization(self, organization_data):
        """
        Create a new organization in Pipedrive
        
        Args:
            organization_data: Organization data to create
        Returns:
            data of the organization
        """
        response = self._make_request("POST", "organizations", json_data=organization_data)
        if not response.get("success"):
            raise Exception(f"Failed to create organization: {response.get('error')}")
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
    
    def create_deal(self, deal_data):
        """
        Create a new deal in Pipedrive
        
        Args:
            deal_data: Deal data to create
            
        Returns:
            Created deal data
        """
        response = self._make_request("POST", "deals", json_data=deal_data)
        
        if not response.get("success"):
            raise Exception(f"Failed to create deal: {response.get('error')}")
        
        return response.get("data", {})
    
    def get_deals(self, limit=100, status=None, sort_by=None, sort_direction='asc', owner_id=None, stage_id=None, filter_id=None):
        """
        Get deals from Pipedrive
        
        Args:
            limit: Maximum number of deals to fetch
            status: Status filter (all_not_deleted, open, won, lost, deleted, all)
            start: Pagination start
            sort: Sort order
            owner_id: Filter by owner ID
            stage_id: Filter by stage ID
            filter_id: Filter ID to apply
            
        Returns:
            List of deals
        """
        params = {
            "limit": limit,
            "status": status,
        }
        
        # Add optional parameters if provided
        if sort_by:
            params["sort_by"] = sort_by
        if sort_direction:
            params["sort_direction"] = sort_direction
        if owner_id:
            params["owner_id"] = int(owner_id)
        if stage_id:
            params["stage_id"] = int(stage_id)
        if filter_id:
            params["filter_id"] = filter_id
        
        response = self._make_request("GET", "deals", params=params)
        
        if not response.get("success"):
            raise Exception(f"Failed to get deals: {response.get('error')}")
        
        return response.get("data", [])

    def get_recently_closed_deals(self, days_back=30, limit=100):
        """
        Get recently closed (won) deals from Pipedrive
        
        Args:
            days_back: Number of days to look back for closed deals
            limit: Maximum number of deals to fetch
            
        Returns:
            List of recently closed deals with organization data
        """
        from datetime import datetime, timedelta
        
        # Get won deals
        deals = self.get_deals(
            limit=limit,
            status="won",
            sort_by="update_time",
            sort_direction="desc"
        )
        
        # Filter by date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_deals = []
        
        for deal in deals:
            # Check if deal was updated recently (this includes when it was won)
            if deal.get("update_time"):
                update_time = datetime.fromisoformat(deal["update_time"].replace("Z", "+00:00"))
                if update_time >= cutoff_date:
                    # Enrich deal with organization data if not already included
                    if deal.get("org_id") and not isinstance(deal["org_id"], dict):
                        try:
                            org_data = self.get_organization_by_id(deal["org_id"])
                            deal["org_id"] = org_data
                        except:
                            # If we can't get org data, skip this deal
                            continue
                    recent_deals.append(deal)
        
        return recent_deals


    def create_prospects_from_lookalikes(self, lookalike_companies, pipeline_id=None, stage_id=None, owner_id=None):
        """
        Create prospect organizations and deals in Pipedrive from lookalike companies
        
        Args:
            lookalike_companies: List of lookalike companies from Surfe
            pipeline_id: Pipeline ID for new deals
            stage_id: Stage ID for new deals  
            owner_id: Owner ID for new deals
            
        Returns:
            List of created prospects with deal and organization IDs
        """
        created_prospects = []
        
        for company in lookalike_companies:
            try:
                # Check if organization already exists
                existing_org = None
                if company.get("name"):
                    existing_org = self.search_organization({
                        "term": company["name"],
                        "fields": "name",
                    })                
                if not existing_org or not existing_org.get("items"):
                    # Create new organization
                    org_data = {
                        "name": company.get("name", "Unknown Company"),
                    }
                    created_org = self.create_organization(org_data)
                    org_id = created_org.get("id")
                else:
                    org_id = existing_org["items"][0]["item"]["id"]
                
                # Create deal for this prospect
                deal_data = {
                    "title": f"Lookalike Prospect - {company.get('name', 'Unknown')}",
                    "org_id": int(org_id),
                    "value": 5000,  # Default prospect value
                    "currency": "USD"
                }
                
                if pipeline_id:
                    deal_data["pipeline_id"] = int(pipeline_id)
                if stage_id:
                    deal_data["stage_id"] = int(stage_id)
                if owner_id:
                    deal_data["owner_id"] = int(owner_id)
                
                created_deal = self.create_deal(deal_data)
                
                prospect_info = {
                    "company": company,
                    "organization_id": org_id,
                    "deal_id": created_deal.get("id"),
                }
                
                created_prospects.append(prospect_info)
                
            except Exception as e:
                print(f"Failed to create prospect for {company.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return created_prospects
    
    def create_activity(self, activity_data):
        """
        Create a new activity in Pipedrive
        
        Args:
            activity_data: Activity data to create
            
        Returns:
            Created activity data
        """
        response = self._make_request("POST", "activities", json_data=activity_data)
        
        if not response.get("success"):
            raise Exception(f"Failed to create activity: {response.get('error')}")
        
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
    
    def format_enriched_data_for_pipedrive(self, enriched_person, event_name=None):
        """
        Format enriched data from Surfe for Pipedrive person creation
        
        Args:
            enriched_person: Enriched person data from Surfe
            event_name: Name of the event/webinar (optional)
            
        Returns:
            Formatted data for Pipedrive person creation
        """
        existing_org = self.search_organization({
            "term": enriched_person.get("companyName", ""),
            "fields": "name",
            "exact_match": True,
            "limit": 1
        })
        if existing_org:
            org = existing_org
        else:
            org = self.create_organization({
                "name": enriched_person.get("companyName", "")
            })
        person_data = {
            "name": f"{enriched_person.get('firstName', '')} {enriched_person.get('lastName', '')}".strip(),
            # "first_name": enriched_person.get("firstName", ""),
            # "last_name": enriched_person.get("lastName", ""),
            # "job_title": enriched_person.get("jobTitle", ""),
            "org_id": org.get("id"),
        }
        person_data["emails"] = [
            {
                "value": email_obj["email"],
                "primary": index == 0
            }
            for index, email_obj in enumerate(enriched_person.get("emails", []))
        ]
        person_data["phones"] = [
            {
                "value": phone_obj["mobilePhone"],
                "primary": index == 0
            }
            for index, phone_obj in enumerate(enriched_person.get("mobilePhones", []))
        ]
        
        return person_data
    
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
    
