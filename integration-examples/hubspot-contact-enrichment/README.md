# HubSpot Contact Enrichment Example

This example demonstrates how to use the Surfe API to enrich contact information directly from HubSpot CRM.

## Overview

The script connects to your HubSpot account, fetches contacts, sends them to the Surfe API for people enrichment, and then updates your HubSpot contacts with the enriched information including email addresses and phone numbers.

## Requirements

- Python 3.6+
- requests library
- python-dotenv library

Install the required packages:

```bash
pip install requests python-dotenv
```

## Environment Variables

You need to create a `.env` file in the same directory as the script with:

```
HUBSPOT_ACCESS_TOKEN=your_hubspot_access_token_here
SURFE_API_KEY=your_surfe_api_key_here
```

## Usage

Simply run the script:

```bash
python main.py
```

The script will:
1. Fetch contacts from your HubSpot account
2. Prepare the data for enrichment
3. Send the data to Surfe's API
4. Poll for enrichment results
5. Update your HubSpot contacts with the enriched data


## API Endpoints Used

This example uses the following API endpoints:

### Surfe API
1. [Enrich People (start)](https://developers.surfe.com/public-003-create-bulk-enrichment) - Starts the enrichment process
2. [Enrich People (get)](https://developers.surfe.com/public-004-get-bulk-enrichment) - Checks the status and retrieves results

### HubSpot API
1. [GET /crm/v3/objects/contacts](https://developers.hubspot.com/docs/reference/api/crm/objects/contacts#get-crm-v3-objects-contacts) - Fetch contacts
2. [POST /crm/v3/objects/contacts/batch/update](https://developers.hubspot.com/docs/reference/api/crm/objects/contacts#post-crm-v3-objects-contacts-batch-update) - Update contacts 