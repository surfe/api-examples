"""
Pipedrive Contact Enrichment Script

This script fetches persons from Pipedrive, enriches them using Surfe API,
and updates the Pipedrive persons with the enriched data.
"""
import os
import sys
import time
from dotenv import load_dotenv

# Add core directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import core services
from core.surfe import SurfeService
from core.integrations.pipedrive import PipedriveService


def main():
    """
    Main function to orchestrate the enrichment process
    """
    load_dotenv()
    pipedrive_api_key = os.getenv("PIPEDRIVE_API_KEY")
    surfe_api_key = os.getenv("SURFE_API_KEY")
    
    if not pipedrive_api_key or not surfe_api_key:
        print("Error: Missing API keys. Please check your .env file.")
        return
    
    try:
        # Initialize the Pipedrive and Surfe services
        pipedrive_service = PipedriveService(pipedrive_api_key)
        surfe_service = SurfeService(surfe_api_key)
        
        # Step 1: Get persons from Pipedrive
        print("Fetching persons from Pipedrive...")
        persons = pipedrive_service.get_persons(
            limit=100,
        )
        print(f"Found {len(persons)} persons to enrich")
        
        if not persons:
            print("No persons found that need enrichment")
            return
        
        # Step 2: Format persons for Surfe API
        print("Preparing data for Surfe enrichment...")
        people_data = pipedrive_service.format_persons_for_surfe(persons)
        
        if not people_data:
            print("No persons with sufficient data for enrichment")
            return
        
        print(f"Prepared {len(people_data)} persons for enrichment")
        
        # Step 3: Prepare and start enrichment process
        surfe_payload = surfe_service.prepare_people_payload(
            people_data, 
            list_name=f"Pipedrive Enrichment {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("Starting Surfe enrichment process...")
        enrichment_id = surfe_service.start_enrichment(surfe_payload)
        print(f"Enrichment started with ID: {enrichment_id}")
        
        # Step 4: Poll for results
        print("Polling for enrichment results...")
        enriched_data = surfe_service.poll_enrichment_status(enrichment_id)
        print("Enrichment completed successfully")
        print(f"Enriched {len(enriched_data.get('people', []))} persons")
        
        # Step 5: Update Pipedrive persons with enriched data
        print("Updating persons in Pipedrive...")
        
        updated_count = 0
        for person in persons:
            person_id = person["id"]
            update_data = pipedrive_service.prepare_person_update_from_surfe(person_id, enriched_data)
            
            if update_data:
                print(f"Updating person {person_id}...")
                pipedrive_service.update_person(person_id, update_data)
                updated_count += 1
        
        print(f"Successfully updated {updated_count} persons in Pipedrive")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()