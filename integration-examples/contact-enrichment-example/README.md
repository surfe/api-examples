# Contact Enrichment Example

This example demonstrates how to use the Surfe API to enrich contact information from a CSV file.

## Overview

The script takes a CSV file with contact information, sends it to the Surfe API for people enrichment, and then creates an output CSV with updated information and a status column indicating what data was updated or filled.

## Input CSV Format

The input CSV should have the following columns:
- First Name
- Last Name
- Company Name
- Company Domain
- Email Address
- Mobile Phone Number
- Job Title
- LinkedIn Profile URL

Not all fields need to be populated for each contact. The enrichment process will attempt to fill in missing information and correct any outdated information. However you need to provide either a linkedinUrl or a combination of "firstName lastName companyName" or combination of "firstName lastName companyWebsite"

## Usage

```bash
python contact_enrichment.py --input sample_input.csv --output enriched_contacts.csv
```

### Environment Variables

You need to create a `.env` file in the same directory as the script with:

```
SURFE_API_KEY=your_api_key_here
```

### Parameters

- `--input`: Path to the input CSV file (required)
- `--output`: Path where the output CSV file will be saved (required)
- `--poll-interval`: How often to check the status of the enrichment job in seconds (default: 5)

## Output

The script produces a CSV file with the same fields as the input plus an additional column:

- `Update Status`: Indicates what fields were updated or filled in during enrichment

## API Endpoints Used

This example uses the following Surfe API endpoints:

1. [Enrich People (start)](https://developers.surfe.com/public-003-create-bulk-enrichment) - Starts the enrichment process
2. [Enrich People (get)](https://developers.surfe.com/public-004-get-bulk-enrichment) - Checks the status and retrieves results

## Requirements

- Python 3.6+
- requests library
- python-dotenv library 