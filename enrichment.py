import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load contacts from CSV
contacts_df = pd.read_csv('contacts.csv')

# Set up API authentication
api_key = os.getenv('SURFE_API_KEY')
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Extract unique company domains directly from email addresses
unique_domains = list(set(contacts_df['Email Address'].apply(lambda x: x.split('@')[-1])))
organizations = [{'domain': domain} for domain in unique_domains]

# Enrich Companies
company_enrich_url = 'https://api.surfe.com/v1/organizations/enrichments/bulk'
company_request_body = {
    'name': 'Enriched Companies',
    'organizations': organizations
}

company_response = requests.post(company_enrich_url, headers=headers, json=company_request_body)
if company_response.status_code != 202:
    print(f"Error: Company enrichment request failed with status code {company_response.status_code}")
    print("Response:", company_response.json())
    exit(1)

company_enrichment_id = company_response.json().get('id')
if not company_enrichment_id:
    print("Error: 'id' not found in company enrichment response")
    exit(1)

# Polling for company enrichment results
company_results_url = f'https://api.surfe.com/v1/organizations/enrichments/bulk/{company_enrichment_id}'
while True:
    company_results_response = requests.get(company_results_url, headers=headers)
    company_results_data = company_results_response.json()
    if company_results_data.get('status') != 'IN_PROGRESS':
        break
    time.sleep(5)

# Map enriched company data
enriched_companies = {}
for org in company_results_data.get('organizations', []):
    domain = org.get('website')
    if domain:
        industries = org.get('industries', [])
        industry = industries[0].get('industry') if industries else 'N/A'
        enriched_companies[domain] = {
            'company_name': org.get('name'),
            'company_industry': industry,
            'company_revenue': org.get('annualRevenueRange')
        }

# Combine enriched data with original contacts
enriched_contacts = []
for index, row in contacts_df.iterrows():
    email_domain = row['Email Address'].split('@')[-1]
    company_info = enriched_companies.get(email_domain, {})
    enriched_contact = {
        'First Name': row['First Name'],
        'Last Name': row['Last Name'],
        'Email Address': row['Email Address'],
        'Job Title': row.get('Job Title'),
        'Company Name': company_info.get('company_name'),
        'Company Industry': company_info.get('company_industry'),
        'Company Revenue': company_info.get('company_revenue')
    }
    enriched_contacts.append(enriched_contact)

# Save enriched contacts to a new CSV file
enriched_contacts_df = pd.DataFrame(enriched_contacts)
enriched_contacts_df = enriched_contacts_df.fillna('N/A')
enriched_contacts_df.to_csv('enriched_contacts.csv', index=False)
