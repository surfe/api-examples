"""
Zoom Webinar Lead Generation and Pipedrive Deals Integration

This script fetches webinar registrants from Zoom, enriches them using Surfe API,
creates persons and deals in Pipedrive with lead scoring and territory assignment.
"""
import json
import os
import sys
import time
from dotenv import load_dotenv

# Add core directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import core services
from core.surfe import SurfeService
from core.integrations.zoom import ZoomService
from core.integrations.pipedrive import PipedriveService

class MockZoomService:
    """Mock Zoom service that returns test data instead of making API calls"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        # Load mock data
        mock_file_path = os.path.join(os.path.dirname(__file__), 'mock_webinar_registrants.json')
        with open(mock_file_path, 'r') as f:
            self.mock_data = json.load(f)
    
    def get_all_webinar_registrants(self, webinar_id):
        """Return mock registrants data"""
        # print(f"🎭 MOCK MODE: Using mock data instead of calling Zoom API for webinar {webinar_id}")
        return self.mock_data['registrants']
    
    def process_webinar_registrants(self, registrants):
        """
        Process registrants to extract first name, last name, email, and company information
        (Same logic as the real ZoomService)
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


def determine_deal_value(enriched_person, webinar_topic):
    """
    Determine deal value based on enriched data and webinar topic
    
    Args:
        enriched_person: Enriched person data from Surfe
        webinar_topic: Topic of the webinar
        
    Returns:
        Deal value in dollars
    """
    base_value = 5000  # Base deal value
    
    # Adjust based on seniority
    seniorities = [s.lower() for s in enriched_person.get("seniorities", [])]
    if "c-level" or "director" or "founder" or "board member" in seniorities:
        base_value *= 3
    elif "vp" or "head" or "owner" or "partner"  in seniorities:
        base_value *= 2.5
    elif "manager" in seniorities:
        base_value *= 1.5
    
    # Adjust based on company size (if available in future)
    # This could be enhanced with company data from Surfe
    
    # Adjust based on webinar topic
    if webinar_topic and any(keyword in webinar_topic.lower() for keyword in ["enterprise", "scale", "growth"]):
        base_value *= 1.5
    
    return int(base_value)


def assign_deal_owner(enriched_person, default_owner_id):
    """
    Assign deal owner based on territory or other criteria
    
    Args:
        enriched_person: Enriched person data from Surfe
        default_owner_id: Default owner ID if no specific assignment
        
    Returns:
        Owner ID for the deal
    """
    # This is a simplified example - in practice, you'd have more complex logic
    # based on geography, industry, company size, etc.
    
    # Example: Assign based on department
    departments = enriched_person.get("departments", [])
    
    # You would replace these with actual user IDs from your Pipedrive
    territory_mapping = {
        "EXECUTIVE": default_owner_id,  # Senior sales rep
        "FINANCE": default_owner_id,    # Finance specialist
        "IT": default_owner_id,         # Technical sales rep
        "SALES": default_owner_id,      # Sales specialist
    }
    
    for dept in departments:
        if dept in territory_mapping:
            return territory_mapping[dept]
    
    return default_owner_id


def main():
    """
    Main function to orchestrate the integration process - MOCK VERSION
    """
    # print("🎭 MOCK MODE: Running integration with mock Zoom data")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    zoom_api_token = os.getenv("ZOOM_API_TOKEN", "mock_token")  # Default for mock mode
    surfe_api_key = os.getenv("SURFE_API_KEY")
    pipedrive_api_key = os.getenv("PIPEDRIVE_API_KEY")
    
    # Get required IDs from environment variables
    webinar_id = os.getenv("ZOOM_WEBINAR_ID", "mock_webinar_123")  # Default for mock mode
    pipeline_id = os.getenv("PIPEDRIVE_PIPELINE_ID")
    stage_id = os.getenv("PIPEDRIVE_STAGE_ID")  # "Webinar Lead" stage
    default_owner_id = os.getenv("PIPEDRIVE_DEFAULT_OWNER_ID")
    
    # Validate required environment variables (relaxed for mock mode)
    if not all([surfe_api_key, pipedrive_api_key, pipeline_id, stage_id]):
        print("Error: Missing required environment variables. Please check your .env file.")
        print("Required: SURFE_API_KEY, PIPEDRIVE_API_KEY, PIPEDRIVE_PIPELINE_ID, PIPEDRIVE_STAGE_ID")
        return
    
    try:
        # Initialize services
        zoom_service = MockZoomService(zoom_api_token)
        surfe_service = SurfeService(surfe_api_key, version="v2")
        pipedrive_service = PipedriveService(pipedrive_api_key)
        
        # Step 1: Fetch webinar registrants from Mock Zoom
        print(f"🎭 Fetching registrants for webinar {webinar_id}...")
        registrants = zoom_service.get_all_webinar_registrants(webinar_id)
        print(f"✅ Found {len(registrants)} mock registrants for the webinar")
        
        # Step 2: Process registrants to extract essential information
        print("📋 Processing registrants to extract name and company information...")
        processed_registrants = zoom_service.process_webinar_registrants(registrants)
        print(f"✅ Found {len(processed_registrants)} registrants with valid name and company information")
        
        if not processed_registrants:
            print("❌ No registrants with valid information found. Exiting...")
            return
        
        # Display sample of processed registrants
        print("\n📊 Sample of processed registrants:")
        for i, registrant in enumerate(processed_registrants[:3]):
            print(f"  {i+1}. {registrant['firstName']} {registrant['lastName']} @ {registrant['companyName']}")
        if len(processed_registrants) > 3:
            print(f"  ... and {len(processed_registrants) - 3} more")
        
        # Step 3: Prepare and start Surfe enrichment
        print("\n🔍 Preparing Surfe enrichment...")
        surfe_payload = surfe_service.prepare_people_payload(
            processed_registrants,
        )
        
        print("🚀 Starting Surfe enrichment process...")
        enrichment_id = surfe_service.start_enrichment(surfe_payload)
        print(f"✅ Enrichment started with ID: {enrichment_id}")
        
        # Step 4: Poll for enrichment results
        print("⏳ Polling for enrichment results...")
        enriched_data = surfe_service.poll_enrichment_status(enrichment_id)
        
        if not enriched_data:
            print("❌ No enriched data received from Surfe. Exiting...")
            return
        
        print(f"✅ Received {len(enriched_data)} enriched profiles from Surfe")
        
        # Step 5: Create persons and deals in Pipedrive
        print("\n💼 Creating persons and deals in Pipedrive...")
        webinar_topic = f"Mock Enterprise Growth Webinar {webinar_id}"  # Mock webinar topic
        
        created_deals = []
        failed_creations = []
        
        # Ensure enriched_data is a list and handle None case
        if not isinstance(enriched_data, list):
            print("❌ No enriched data received from Surfe. Exiting...")
            enriched_data = []
        
        for enriched_person in enriched_data:
            try:            
                # Determine deal value
                deal_value = determine_deal_value(enriched_person, webinar_topic)
                # Assign deal owner
                deal_owner_id = assign_deal_owner(enriched_person, default_owner_id)
                # Check if person already exists in Pipedrive
                emails = enriched_person.get("emails", [])
                primary_email = emails[0].get("email") if emails else None
                if not primary_email:
                    print(f"⚠️  Skipping {enriched_person.get('firstName', 'Unknown')} {enriched_person.get('lastName', 'Unknown')} - no email found")
                    continue
                existing_person = pipedrive_service.find_person_by_email(primary_email)
                if existing_person:
                    person_id = existing_person['id']
                    print(f"👤 Found existing person: {enriched_person.get('firstName')} {enriched_person.get('lastName')} (ID: {person_id})")
                else:
                    # Create new person in Pipedrive
                    person_data = pipedrive_service.format_enriched_data_for_pipedrive(enriched_person)
                    person_response = pipedrive_service.create_person(person_data)
                    person_id = person_response['id']
                    print(f"✅ Created new person: {enriched_person.get('firstName')} {enriched_person.get('lastName')} (ID: {person_id})")
                
                person_data = pipedrive_service.format_enriched_data_for_pipedrive(enriched_person)
                # Create deal
                deal_data = {
                    'title': f"Webinar Lead - {enriched_person.get('firstName')} {enriched_person.get('lastName')}",
                    'owner_id': int(deal_owner_id),
                    'person_id': int(person_id),
                    'org_id': person_data.get("org_id", None),
                    'pipeline_id': int(pipeline_id),
                    'stage_id': int(stage_id),
                    'value': deal_value,
                    'currency': 'USD',
                    'status': 'open',
                    'expected_close_date': time.strftime('%Y-%m-%d', time.gmtime(time.time() + 30*24*3600)),  # 30 days from now
                }
                deal_response = pipedrive_service.create_deal(deal_data)
                deal_id = deal_response['id']
                # Create follow-up activity
                activity_data = {
                    'subject': f'Follow up on webinar attendance - {enriched_person.get("firstName")} {enriched_person.get("lastName")}',
                    'type': 'call',
                    'owner_id': int(deal_owner_id),
                    'deal_id': int(deal_id),
                    'org_id': person_data.get("org_id", None),
                    'due_date': time.strftime('%Y-%m-%d', time.gmtime(time.time() + 2*24*3600)),  # 2 days from now
                    'due_time': '10:00',
                    'duration': '00:30',
                    'participants': [
                        {
                            'person_id': int(person_id),
                            'primary': True
                        }
                    ],
                    'note': f'Follow up call for webinar attendee. Interested in: {webinar_topic}'
                }
                activity_response = pipedrive_service.create_activity(activity_data)
                created_deals.append({
                    'person_name': f"{enriched_person.get('firstName')} {enriched_person.get('lastName')}",
                    'company': enriched_person.get('companyName', 'Unknown'),
                    'deal_id': deal_id,
                    'deal_value': deal_value,
                    'activity_id': activity_response['id']
                })
                
                print(f"💰 Created deal (ID: {deal_id}) worth ${deal_value:,} ")
                
            except Exception as e:
                error_msg = f"Failed to create deal for {enriched_person.get('firstName', 'Unknown')} {enriched_person.get('lastName', 'Unknown')}: {str(e)}"
                print(f"❌ {error_msg}")
                failed_creations.append(error_msg)
                continue
        
        # Step 6: Summary
        print("\n" + "="*60)
        print("📊 INTEGRATION SUMMARY")
        print("="*60)
        print(f"🎭 Mock Webinar ID: {webinar_id}")
        print(f"👥 Total Registrants: {len(registrants)}")
        print(f"✅ Processed Registrants: {len(processed_registrants)}")
        print(f"🔍 Enriched Profiles: {len(enriched_data)}")
        print(f"💼 Deals Created: {len(created_deals)}")
        print(f"❌ Failed Creations: {len(failed_creations)}")
        
        if created_deals:
            total_pipeline_value = sum(deal['deal_value'] for deal in created_deals)
            print(f"💰 Total Pipeline Value: ${total_pipeline_value:,}")
            
            print(f"\n🏆 Top 3 Deals by Value:")
            top_deals = sorted(created_deals, key=lambda x: x['deal_value'], reverse=True)[:3]
            for i, deal in enumerate(top_deals, 1):
                print(f"  {i}. {deal['person_name']} @ {deal['company']} - ${deal['deal_value']:,}")
        
        if failed_creations:
            print(f"\n⚠️  Failed Creations:")
            for error in failed_creations:
                print(f"  - {error}")
        
        print(f"\n✅ Integration completed successfully!")
        print(f"🔗 Check your Pipedrive dashboard to see the new deals and activities.")
        
    except Exception as e:
        print(f"❌ Error during integration: {str(e)}")
        raise


if __name__ == "__main__":
    main() 