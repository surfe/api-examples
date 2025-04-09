import os
import time
import requests
from dotenv import load_dotenv

def get_hubspot_contacts(api_key):
    """
    Fetch contacts from HubSpot that need enrichment
    """
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {
        "properties": ["firstname", "lastname", "company", "hs_email_domain", "email", "phone", "jobtitle", "hs_linkedin_url"],
        "limit": 100
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["results"]

def prepare_surfe_payload(hubspot_contacts):
    """
    Prepare contacts for Surfe enrichment API
    """
    people = []
    
    for contact in hubspot_contacts:
        properties = contact.get("properties", {})
        
        person = {
            "externalID": contact["id"],  # Use HubSpot ID as external ID
            "firstName": properties.get("firstname", ""),
            "lastName": properties.get("lastname", ""),
            "companyName": properties.get("company", ""),
            "companyWebsite": properties.get("hs_email_domain", ""),
            "linkedinUrl": properties.get("hs_linkedin_url", "")
        }
        
        # Only add if we have enough data to enrich
        if (person["linkedinUrl"] or 
            (person["firstName"] and person["lastName"] and person["companyName"]) or
            (person["firstName"] and person["lastName"] and person["companyWebsite"])):
            people.append(person)
    
    return {
        "enrichmentType": "emailAndMobile",
        "listName": f"HubSpot Enrichment {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "people": people
    }

def start_surfe_enrichment(api_key, payload):
    """
    Start the bulk enrichment process with Surfe API
    """
    url = "https://api.surfe.com/v1/people/enrichments/bulk"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["id"]

def poll_enrichment_status(api_key, enrichment_id, max_attempts=60, delay=5):
    """
    Poll the enrichment status until it's complete
    """
    url = f"https://api.surfe.com/v1/people/enrichments/bulk/{enrichment_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    attempts = 0
    while attempts < max_attempts:
        response = requests.get(url, headers=headers)
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

def prepare_hubspot_update_data(enriched_data):
    """
    Prepare data for HubSpot update by comparing original and enriched data
    """
    update_data = []
    
    for person in enriched_data.get("people", []):
        # Extract the best email and phone
        email = None
        if person.get("emails"):
            # Sort by validation status and take the first one
            sorted_emails = sorted(
                person["emails"], 
                key=lambda x: 0 if x.get("validationStatus") == "VALID" else 1
            )
            if sorted_emails:
                email = sorted_emails[0].get("email")
        
        mobile_phone = None
        if person.get("mobilePhones"):
            # Sort by confidence score and take the highest
            sorted_phones = sorted(
                person["mobilePhones"], 
                key=lambda x: x.get("confidenceScore", 0), 
                reverse=True
            )
            if sorted_phones:
                mobile_phone = sorted_phones[0].get("mobilePhone")
        
        # Only update if we have new data
        properties = {}
        if email:
            properties["email"] = email
        if mobile_phone:
            properties["phone"] = mobile_phone
        if person.get("jobTitle"):
            properties["jobtitle"] = person["jobTitle"]
        if person.get("linkedinUrl"):
            properties["hs_linkedin_url"] = person["linkedinUrl"]
        
        # Only add to update list if we have properties to update
        if properties:
            update_data.append({
                "id": person["externalID"],
                "properties": properties
            })
    
    return update_data

def update_hubspot_contacts(api_key, update_data):
    """
    Update contacts in HubSpot with enriched data
    """
    if not update_data:
        print("No contacts to update")
        return {"status": "skipped", "message": "No contacts to update"}
    
    url = "https://api.hubapi.com/crm/v3/objects/contacts/batch/update"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    batch_size = 100
    results = []
    
    for i in range(0, len(update_data), batch_size):
        batch = update_data[i:i + batch_size]
        payload = {"inputs": batch}
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results.append(response.json())
    
    return {
        "status": "success",
        "updated_contacts": len(update_data),
        "results": results
    }

def main():
    """
    Main function to orchestrate the enrichment process
    """
    load_dotenv()
    hubspot_api_key = os.getenv("HUBSPOT_ACCESS_TOKEN")
    surfe_api_key = os.getenv("SURFE_API_KEY")
    
    if not hubspot_api_key or not surfe_api_key:
        print("Error: Missing API keys. Please check your .env file.")
        return
    
    try:
        # Step 1: Get contacts from HubSpot
        print("Fetching contacts from HubSpot...")
        hubspot_contacts = get_hubspot_contacts(hubspot_api_key)
        print(f"Found {len(hubspot_contacts)} contacts to enrich")
        
        if not hubspot_contacts:
            print("No contacts found that need enrichment")
            return
        
        # Step 2: Prepare payload for Surfe API
        print("Preparing data for Surfe enrichment...")
        surfe_payload = prepare_surfe_payload(hubspot_contacts)
        
        if not surfe_payload["people"]:
            print("No contacts with sufficient data for enrichment")
            return
        
        # Step 3: Start enrichment process
        print("Starting Surfe enrichment process...")
        enrichment_id = start_surfe_enrichment(surfe_api_key, surfe_payload)
        print(f"Enrichment started with ID: {enrichment_id}")
        
        # Step 4: Poll for results
        print("Polling for enrichment results...")
        enriched_data = poll_enrichment_status(surfe_api_key, enrichment_id)
        print("Enrichment completed successfully")
        
        # Step 5: Prepare data for HubSpot update
        print("Preparing data for HubSpot update...")
        update_data = prepare_hubspot_update_data(enriched_data)
        print(f"Prepared {len(update_data)} contacts for update")
        
        # Step 6: Update HubSpot contacts
        print("Updating contacts in HubSpot...")
        update_result = update_hubspot_contacts(hubspot_api_key, update_data)
        print(f"Update completed: {update_result['status']}")
        print(f"Updated {update_result.get('updated_contacts', 0)} contacts")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()