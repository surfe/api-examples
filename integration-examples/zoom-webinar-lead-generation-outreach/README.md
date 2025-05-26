# Zoom Webinar Lead Generation with Outreach Integration

This integration example demonstrates how to:
1. Fetch webinar registrants from Zoom API
2. Process registrants to extract name and company information
3. Enrich leads with Surfe API
4. Create prospects in Outreach
5. Add prospects to an Outreach sequence for follow-up

## Prerequisites

- Zoom API credentials (JWT or OAuth token)
- Surfe API key
- Outreach OAuth access token
- A Zoom webinar ID with registrants (with valid name and company information)
- An Outreach sequence ID for lead follow-up
- An Outreach mailbox ID to send sequence messages from

## Setup

1. Clone the repository
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy the `env.sample` file to `.env` and fill in your API credentials:
   ```
   cp env.sample .env
   ```

## Environment Variables

- `ZOOM_API_TOKEN`: Your Zoom JWT or OAuth token
- `ZOOM_WEBINAR_ID`: The ID of the webinar to fetch registrants from
- `SURFE_API_KEY`: Your Surfe API key
- `OUTREACH_ACCESS_TOKEN`: Your Outreach OAuth access token
- `OUTREACH_SEQUENCE_ID`: The ID of the Outreach sequence to add prospects to
- `OUTREACH_MAILBOX_ID`: The ID of the Outreach mailbox to use for sending

## Usage

Run the script to execute the full workflow:

```
python main.py
```

## Flow Overview

1. The script fetches all registrants from a specified Zoom webinar
2. Registrants are processed to extract first name, last name, and company information
3. The processed registrants are sent to Surfe API for enrichment (emails, phone numbers, etc.)
4. Enriched data is used to create prospects in Outreach (or update if they already exist)
5. Each prospect is added to a specified Outreach sequence for automated follow-up

## Notes

- The script handles pagination for Zoom API endpoints
- Registrants without first name, last name, or company information are skipped
- Enrichment through Surfe is done asynchronously with polling
- The script deduplicates prospects in Outreach based on email address
- Error handling is implemented throughout the workflow 