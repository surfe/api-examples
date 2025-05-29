
import os
import sys
from dotenv import load_dotenv

# Add core directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import core services
from core.surfe import SurfeService
from core.integrations.pipedrive import PipedriveService

def main():
    load_dotenv()
    
    # Get API keys from environment
    pipedrive_api_key = os.getenv("PIPEDRIVE_API_KEY")
    surfe_api_key = os.getenv("SURFE_API_KEY")
    
    # Pipedrive configuration
    pipeline_id = os.getenv("PIPEDRIVE_PIPELINE_ID")  # Optional: specific pipeline for prospects
    stage_id = os.getenv("PIPEDRIVE_STAGE_ID")  # Optional: specific stage for prospects
    owner_id = os.getenv("PIPEDRIVE_DEFAULT_OWNER_ID")  # Optional: default owner for prospects
           
    days_back = 30  
    max_lookalikes = 10 
    
    if not pipedrive_api_key or not surfe_api_key:
        print("❌ Error: Missing API keys. Please check your .env file.")
        return
    
    try:
        # Initialize services
        print("🚀 Initializing services...")
        pipedrive_service = PipedriveService(pipedrive_api_key)
        surfe_service = SurfeService(surfe_api_key, version="v1")
        
        # Step 1: Get recently closed deals from Pipedrive
        print(f"📊 Fetching recently closed deals from last {days_back} days...")
        recent_deals = pipedrive_service.get_recently_closed_deals(days_back=days_back, limit=100)
        
        
        
        if not recent_deals:
            print(f"❌ No closed deals found in the last {days_back} days.")
            return
        
        print(f"✅ Found {len(recent_deals)} recently closed deals")
        
        # Step 2: Extract company domains from deals
        print("🔍 Extracting company domains from closed deals...")
        company_domains = surfe_service.extract_companies_from_deals(recent_deals)
        
        if not company_domains:
            print("❌ No company domains could be extracted from recent deals.")
            return
        
        print(f"✅ Extracted {len(company_domains)} unique company domains")
        print("📋 Sample domains:", ", ".join(company_domains[:5]))
        if len(company_domains) > 5:
            print(f"   ... and {len(company_domains) - 5} more")
        
        # Step 3: Find lookalike companies using Surfe API
        print(f"🎯 Searching for lookalike companies (max {max_lookalikes})...")
        lookalike_results = surfe_service.search_company_lookalikes(
            company_domains=company_domains,
            limit=max_lookalikes
        )
        
        lookalike_companies = lookalike_results.get("organizations", [])
        
        if not lookalike_companies:
            print("❌ No lookalike companies found.")
            return
        
        print(f"✅ Found {len(lookalike_companies)} lookalike companies")
        
    
        
        # # Step 4: Create prospects in Pipedrive
        create_prospects = input("📝 Create these prospects in Pipedrive? (y/N): ").lower().strip()
        
        if create_prospects == 'y':
            print("\n💼 Creating prospect organizations and deals in Pipedrive...")
            
            created_prospects = pipedrive_service.create_prospects_from_lookalikes(
                lookalike_companies=lookalike_companies,
                pipeline_id=pipeline_id,
                stage_id=stage_id,
                owner_id=owner_id
            )
            
            if created_prospects:
                print(f"✅ Successfully created {len(created_prospects)} prospects in Pipedrive")
                
                # Calculate total pipeline value
                total_value = len(created_prospects) * 5000  # Default $5000 per prospect
                
                print(f"\n📊 INTEGRATION SUMMARY:")
                print("=" * 50)
                print(f"Source deals analyzed: {len(recent_deals)}")
                print(f"Company domains extracted: {len(company_domains)}")
                print(f"Lookalike companies found: {len(lookalike_companies)}")
                print(f"Prospects created in Pipedrive: {len(created_prospects)}")
                print(f"Total pipeline value: ${total_value:,}")
                print(f"Time period analyzed: Last {days_back} days")
            else:
                print("❌ No prospects were created in Pipedrive")
        else:
            print("ℹ️  Prospect creation skipped. You can run the script again to create prospects.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 