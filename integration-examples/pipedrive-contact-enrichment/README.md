# Pipedrive Contact Enrichment

This example demonstrates how to enrich contact information in Pipedrive using the Surfe API.

## Overview

The script automatically:
1. Fetches persons from your Pipedrive account
2. Enriches their information using the Surfe API
3. Updates the persons in Pipedrive with the enriched data


## Setup

1. create a virtual environment
    ```bash
    python3 -m venv env
    source env/bin/activate 
    ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   PIPEDRIVE_API_KEY=your_pipedrive_api_key
   SURFE_API_KEY=your_surfe_api_key
   ```

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Fetch persons from Pipedrive
2. Prepare them for enrichment
3. Send them to Surfe API
4. Poll for results
5. Update Pipedrive with enriched data


## API Endpoints Used

This example uses the following APIs:

1. [Pipedrive API](https://developers.pipedrive.com/docs/api/v1) - For contact management
2. [Surfe API](https://developers.surfe.com/) - For contact enrichment

## Requirements

- Python 3.6+
- Pipedrive API key
- Surfe API key
- requests library
- python-dotenv library

## Rate Limiting

Both Pipedrive and Surfe APIs have rate limits. The script includes built-in rate limit handling, but you should be aware of:
- Pipedrive API limits: [Pipedrive API Limits](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting)
- Surfe API limits: [Surfe API Limits](https://developers.surfe.com/rate-limits)