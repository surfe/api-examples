#!/usr/bin/env python3
import argparse
import csv
import json
import os
import requests
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoints
BULK_ENRICHMENT_ENDPOINT = "https://api.surfe.com/v1/people/enrichments/bulk"
GET_BULK_ENRICHMENT_ENDPOINT = "https://api.surfe.com/v1/people/enrichments/bulk/"

def create_enrichment_payload(input_file: str) -> List[Dict[str, str]]:
    """
    Parse the input CSV file and create the payload for the bulk enrichment API.
    """
    people = []
    
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            person = {
                "firstName": row["First Name"],
                "lastName": row["Last Name"],
                "companyName": row["Company Name"],
                "companyWebsite": row["Company Domain"],
                "externalID": f"{row['First Name']}_{row['Last Name']}".lower().replace(" ", "_"),
                "linkedinUrl": row["LinkedIn Profile URL"]
            }
            # Remove empty fields
            person = {k: v for k, v in person.items() if v}
            people.append(person)
    
    return people

def start_bulk_enrichment(api_key: str, people: List[Dict[str, str]]) -> str:
    """
    Start a bulk enrichment job and return the job ID.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "enrichmentType": "emailAndMobile",
        "listName": f"Contact Enrichment {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "people": people
    }
    
    response = requests.post(
        BULK_ENRICHMENT_ENDPOINT,
        headers=headers,
        json=payload
    )
    
    if response.status_code != 202:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    response_data = response.json()
    return response_data["id"]

def check_enrichment_status(api_key: str, job_id: str) -> Dict[str, Any]:
    """
    Check the status of a bulk enrichment job.
    """
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    response = requests.get(
        f"{GET_BULK_ENRICHMENT_ENDPOINT}{job_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    return response.json()

def compare_and_update_data(original_data: List[Dict[str, str]], enriched_people: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compare original data with enriched data to fill gaps and update incorrect information.
    """
    updated_data = []
    
    # Create a mapping of original data by external ID
    original_map = {}
    for person in original_data:
        key = person.get("externalID", "").lower()
        if not key and "firstName" in person and "lastName" in person:
            key = f"{person['firstName']}_{person['lastName']}".lower().replace(" ", "_")
        original_map[key] = person
    
    for enriched in enriched_people:
        # Find the corresponding original contact
        external_id = enriched.get("externalID", "").lower()
        original = original_map.get(external_id, {})
        
        # Extract email from the emails array
        email = ""
        if "emails" in enriched and enriched["emails"]:
            for email_obj in enriched["emails"]:
                if email_obj.get("validationStatus") == "VALID":
                    email = email_obj.get("email", "")
                    break
            if not email and enriched["emails"]:
                email = enriched["emails"][0].get("email", "")
        
        # Extract mobile phone from the mobilePhones array
        mobile_phone = ""
        if "mobilePhones" in enriched and enriched["mobilePhones"]:
            # Sort by confidence score if available
            sorted_phones = sorted(
                enriched["mobilePhones"], 
                key=lambda x: x.get("confidenceScore", 0), 
                reverse=True
            )
            mobile_phone = sorted_phones[0].get("mobilePhone", "")
        
        # Create updated record with comparison information
        updated = {
            "First Name": enriched.get("firstName", original.get("firstName", "")),
            "Last Name": enriched.get("lastName", original.get("lastName", "")),
            "Company Name": enriched.get("companyName", original.get("companyName", "")),
            "Company Domain": enriched.get("companyWebsite", original.get("companyWebsite", "")),
            "Email Address": email,
            "Mobile Phone Number": mobile_phone,
            "Job Title": enriched.get("jobTitle", original.get("jobTitle", "")),
            "LinkedIn Profile URL": enriched.get("linkedinUrl", original.get("linkedinUrl", "")),
            "Update Status": determine_update_status(original, enriched, email, mobile_phone)
        }
        
        updated_data.append(updated)
    
    return updated_data

def determine_update_status(original: Dict[str, str], enriched: Dict[str, Any], email: str, mobile_phone: str) -> str:
    """
    Determine the update status for a contact by comparing original and enriched data.
    """
    field_mapping = {
        "firstName": "First Name",
        "lastName": "Last Name",
        "companyName": "Company Name", 
        "companyWebsite": "Company Domain",
        "jobTitle": "Job Title",
        "linkedinUrl": "LinkedIn Profile URL"
    }
    
    # Special handling for email and phone which are in arrays in the API response
    special_fields = {
        "email": "Email Address",
        "mobilePhone": "Mobile Phone Number"
    }
    
    updates = []
    filled_gaps = []
    
    # Check regular fields
    for api_field, csv_field in field_mapping.items():
        orig_value = original.get(api_field, "")
        new_value = enriched.get(api_field, "")
        
        # Skip if both are empty or there's no change
        if (not orig_value and not new_value) or orig_value == new_value:
            continue
        
        # Check if we filled a gap
        if not orig_value and new_value:
            filled_gaps.append(csv_field)
        # Check if information was updated
        elif orig_value and new_value and orig_value != new_value:
            updates.append(csv_field)
    
    # Check email
    orig_email = original.get("email", "")
    if orig_email != email:
        if not orig_email and email:
            filled_gaps.append("Email Address")
        elif orig_email and email and orig_email != email:
            updates.append("Email Address")
    
    # Check mobile phone
    orig_phone = original.get("phone", "")
    if orig_phone != mobile_phone:
        if not orig_phone and mobile_phone:
            filled_gaps.append("Mobile Phone Number")
        elif orig_phone and mobile_phone and orig_phone != mobile_phone:
            updates.append("Mobile Phone Number")
    
    if updates and filled_gaps:
        return f"Updated: {', '.join(updates)}; Filled: {', '.join(filled_gaps)}"
    elif updates:
        return f"Updated: {', '.join(updates)}"
    elif filled_gaps:
        return f"Filled: {', '.join(filled_gaps)}"
    else:
        return "No changes"

def save_output_csv(output_file: str, data: List[Dict[str, Any]]):
    """
    Save the updated data to a CSV file.
    """
    if not data:
        return
    
    fieldnames = list(data[0].keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description="Enrich contact information using Surfe API")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds")
    args = parser.parse_args()
    
    api_key = os.getenv('SURFE_API_KEY')
    if not api_key:
        print("Error: SURFE_API_KEY environment variable not set. Please set it or create a .env file.")
        return 1

    try:
        # Parse input file and create payload
        print(f"Parsing input file: {args.input}")
        people = create_enrichment_payload(args.input)
        print(f"Found {len(people)} contacts to enrich")
        
        # Start bulk enrichment
        print("Starting bulk enrichment job...")
        job_id = start_bulk_enrichment(api_key, people)
        print(f"Enrichment job started with ID: {job_id}")
        
        # Poll for results
        print("Waiting for enrichment job to complete...")
        while True:
            status_data = check_enrichment_status(api_key, job_id)
            
            if status_data["status"] == "COMPLETED":
                print("Enrichment job completed successfully")
                enriched_people = status_data["people"]
                break
            elif status_data["status"] == "FAILED":
                raise Exception(f"Enrichment job failed: {status_data.get('error', 'Unknown error')}")
            
            print(f"Job status: {status_data['status']}. Waiting {args.poll_interval} seconds...")
            time.sleep(args.poll_interval)
        
        # Compare and update data
        print("Comparing original data with enriched data...")
        updated_data = compare_and_update_data(people, enriched_people)
        
        # Save output to CSV
        print(f"Saving updated data to: {args.output}")
        save_output_csv(args.output, updated_data)
        
        print("Contact enrichment completed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 