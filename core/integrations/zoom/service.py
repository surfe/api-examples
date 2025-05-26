"""
Zoom API Service Module
"""
import requests
import json
from urllib.parse import urljoin


class ZoomService:
    """Service for interacting with the Zoom API"""
    
    def __init__(self, api_token, api_base_url="https://api.zoom.us/v2"):
        self.api_token = api_token
        self.api_base_url = api_base_url
        
    def _make_request(self, method, endpoint, params=None, data=None, json_data=None):
        """
        Make a request to the Zoom API
        
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
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
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
    
    def get_webinar_details(self, webinar_id):
        """
        Get details of a webinar
        
        Args:
            webinar_id: ID of the webinar
            
        Returns:
            Details of the webinar
        """
        endpoint = f"webinars/{webinar_id}"
        response = self._make_request("GET", endpoint)
        return response
    
    def get_webinar_registrants(self, webinar_id, page_size=100, next_page_token=None):
        """
        Get a list of registrants for a webinar
        
        Args:
            webinar_id: ID of the webinar
            page_size: Number of records per page
            next_page_token: Token for pagination
            
        Returns:
            List of webinar registrants
        """
        endpoint = f"webinars/{webinar_id}/registrants"
        params = {
            "page_size": page_size
        }
        
        if next_page_token:
            params["next_page_token"] = next_page_token
            
        response = self._make_request("GET", endpoint, params=params)
        return response
    
    def get_all_webinar_registrants(self, webinar_id, page_size=100):
        """
        Get all registrants for a webinar with pagination handling
        
        Args:
            webinar_id: ID of the webinar
            page_size: Number of records per page
            
        Returns:
            List of all webinar registrants
        """
        all_registrants = []
        next_page_token = None
        
        while True:
            response = self.get_webinar_registrants(webinar_id, page_size, next_page_token)
            registrants = response.get("registrants", [])
            all_registrants.extend(registrants)
            
            next_page_token = response.get("next_page_token")
            if not next_page_token:
                break
                
        return all_registrants
    
    def get_webinar_participants(self, webinar_id, page_size=100, next_page_token=None):
        """
        Get a list of participants for a webinar (post-event)
        
        Args:
            webinar_id: ID of the webinar
            page_size: Number of records per page
            next_page_token: Token for pagination
            
        Returns:
            List of webinar participants
        """
        endpoint = f"report/webinars/{webinar_id}/participants"
        params = {
            "page_size": page_size
        }
        
        if next_page_token:
            params["next_page_token"] = next_page_token
            
        response = self._make_request("GET", endpoint, params=params)
        return response
    
    def get_all_webinar_participants(self, webinar_id, page_size=100):
        """
        Get all participants for a webinar with pagination handling
        
        Args:
            webinar_id: ID of the webinar
            page_size: Number of records per page
            
        Returns:
            List of all webinar participants
        """
        all_participants = []
        next_page_token = None
        
        while True:
            response = self.get_webinar_participants(webinar_id, page_size, next_page_token)
            participants = response.get("participants", [])
            all_participants.extend(participants)
            
            next_page_token = response.get("next_page_token")
            if not next_page_token:
                break
                
        return all_participants
    
    def process_webinar_registrants(self, registrants):
        """
        Process registrants to extract first name, last name, email, and company information
        
        Args:
            registrants: List of registrants from Zoom API
            
        Returns:
            List of processed registrants with required information
        """
        processed_registrants = []
        
        for registrant in registrants:            
            # Skip registrants without first name, last name, or company
            if not (registrant.get("first_name") and registrant.get("last_name") and (registrant.get("org") or registrant.get("email"))):
                continue

            if registrant.get("email"):
                companyDomain = registrant.get("email").split("@")[1]
            else:
                companyDomain = None
                
            processed_registrants.append({
                "firstName": registrant.get("first_name", ""),
                "lastName": registrant.get("last_name", ""),
                "companyName": registrant.get("org", ""),
                "companyDomain": companyDomain
            })
                
        return processed_registrants 