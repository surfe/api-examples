"""
Zoom Webinar Lead Generation and Outreach Integration

This script fetches webinar registrants from Zoom, enriches them using Surfe API,
and adds them to an Outreach sequence for follow-up.
"""
import os
import sys
import time
from dotenv import load_dotenv

# Add core directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import core services
from core.surfe import SurfeService
from core.integrations.zoom import ZoomService
from core.integrations.outreach import OutreachService


def main():
    """
    Main function to orchestrate the integration process
    """
    # Load environment variables
    load_dotenv()
    zoom_api_token = os.getenv("ZOOM_API_TOKEN")
    surfe_api_key = os.getenv("SURFE_API_KEY")
    outreach_access_token = os.getenv("OUTREACH_ACCESS_TOKEN")
    
    # Get required IDs from environment variables
    webinar_id = os.getenv("ZOOM_WEBINAR_ID")
    sequence_id = os.getenv("OUTREACH_SEQUENCE_ID")
    mailbox_id = os.getenv("OUTREACH_MAILBOX_ID")
    
    # Validate required environment variables
    if not all([zoom_api_token, surfe_api_key, outreach_access_token, webinar_id, sequence_id, mailbox_id]):
        print("Error: Missing required environment variables. Please check your .env file.")
        return
    
    try:
        # Initialize services
        zoom_service = ZoomService(zoom_api_token)
        surfe_service = SurfeService(surfe_api_key, version="v2")
        outreach_service = OutreachService(outreach_access_token)
        
        # Step 1: Fetch webinar registrants from Zoom
        print(f"Fetching registrants for webinar {webinar_id}...")
        registrants = zoom_service.get_all_webinar_registrants(webinar_id)
        print(f"Found {len(registrants)} registrants for the webinar")
        
        # Step 2: Process registrants to extract essential information
        print("Processing registrants to extract name and company information...")
        processed_registrants = zoom_service.process_webinar_registrants(registrants)
        print(f"Found {len(processed_registrants)} registrants with valid name and company information")
        
        if not processed_registrants:
            print("No registrants with valid information found. Exiting...")
            return
        
        # Step 3: Prepare and start Surfe enrichment
        print("Preparing Surfe enrichment...")
        surfe_payload = surfe_service.prepare_people_payload(
            processed_registrants,
        )
        
        print("Starting Surfe enrichment process...")
        enrichment_id = surfe_service.start_enrichment(surfe_payload)
        print(f"Enrichment started with ID: {enrichment_id}")
        
        # Step 4: Poll for enrichment results
        print("Polling for enrichment results...")
        enriched_data = surfe_service.poll_enrichment_status(enrichment_id)
        print("Enrichment completed successfully")
        
        enriched_people = enriched_data.get("people", [])
        print(f"Enriched {len(enriched_people)} registrants")
        
        # Step 5: Create prospects in Outreach and add to sequence
        print("Adding enriched registrants to Outreach...")

        event_name = zoom_service.get_webinar_details(webinar_id).get("topic")
        
        success_count = 0
        for person in enriched_people:
            try:
                # Format the enriched data for Outreach
                prospect_data = outreach_service.format_enriched_data_for_outreach(person, event_name)
                
                # Check if we have a valid email
                if not prospect_data.get("emails"):
                    print(f"Skipping {person.get('firstName')} {person.get('lastName')} - No valid email found")
                    continue
                
                # Check if prospect already exists in Outreach
                existing_prospect = outreach_service.find_prospect_by_email(prospect_data["emails"])
                
                if existing_prospect:
                    prospect_id = existing_prospect["id"]
                    print(f"Prospect {person.get('firstName')} {person.get('lastName')} already exists with ID: {prospect_id}")
                else:
                    # Create a new prospect
                    print(f"Creating prospect for {person.get('firstName')} {person.get('lastName')}...")
                    prospect_response = outreach_service.create_prospect(prospect_data)
                    prospect_id = prospect_response["data"]["id"]
                    print(f"Created prospect with ID: {prospect_id}")
                
                # Add the prospect to the sequence
                print(f"Adding prospect {prospect_id} to sequence {sequence_id}...")
                outreach_service.add_prospect_to_sequence(prospect_id, sequence_id, mailbox_id)
                print(f"Successfully added prospect to sequence")
                
                success_count += 1
                
            except Exception as e:
                print(f"Error processing {person.get('firstName')} {person.get('lastName')}: {str(e)}")
        
        print(f"Successfully added {success_count} prospects to Outreach sequence {sequence_id}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 