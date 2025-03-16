import requests
import pandas as pd
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.environ['SURFE_API_KEY']

# Read contacts from CSV
contacts_df = pd.read_csv('contacts.csv')

# Prepare data for enrichment
contacts = []
for index, row in contacts_df.iterrows():
    email_domain = row['Email Address'].split('@')[-1]
    contact = {
        'firstName': row['First Name'],
        'lastName': row['Last Name'],
        'companyWebsite': email_domain,
        'externalID': str(index)  # To match responses with original data
    }
    contacts.append(contact)

# Start bulk enrichment
enrich_url = 'https://api.surfe.com/v1/people/enrichments/bulk'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Create the request body with all required fields
request_body = {
    'enrichmentType': 'email',  
    'listName': 'Enriched Contacts',  
    'people': contacts
}

response = requests.post(enrich_url, headers=headers, json=request_body)
response_data = response.json()

# Add error handling and debugging
if response.status_code != 202:
    print(f"Error: API request failed with status code {response.status_code}")
    print("Response:", response_data)
    exit(1)


try:
    enrichment_id = response_data['id']
except KeyError:
    print("Error: 'id' not found in response data")
    print("Response data received:", response_data)
    exit(1)

# Poll for enrichment results
results_url = f'https://api.surfe.com/v1/people/enrichments/bulk/{enrichment_id}'
while True:
    results_response = requests.get(results_url, headers=headers)
    results_data = results_response.json()
    if results_data['status'] != 'IN_PROGRESS':
        break
    time.sleep(5)  # Wait before polling again

# Process enriched data
enriched_contacts = results_data.get('people', [])
print(enriched_contacts)
for enriched in enriched_contacts:
    external_id = int(enriched['externalID'])
    contacts_df.at[external_id, 'Company Name'] = enriched.get('companyName', 'N/A')
    contacts_df.at[external_id, 'Company Domain'] = enriched.get('companyWebsite', 'N/A')

# Save enriched data to a new CSV
contacts_df.to_csv('enriched_contacts.csv', index=False)
