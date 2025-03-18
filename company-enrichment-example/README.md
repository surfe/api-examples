# Contact Enrichment Script

This Python script enriches contact information by fetching additional company data using the Surfe API. It processes a CSV file containing contact information and adds company-related details such as company name, industry, and revenue range.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install pandas requests python-dotenv
   ```

## Configuration

1. Create a `.env` file in the root directory
2. Add your Surfe API key:
   ```
   SURFE_API_KEY=your_api_key_here
   ```

## Input Data Format

Create a `contacts.csv` file with the following columns:
- First Name
- Last Name
- Email Address
- Job Title (optional)

## Usage

1. Place your `contacts.csv` file in the same directory as the script
2. Run the script:
   ```bash
   python enrichment.py
   ```

## Output

The script will generate an `enriched_contacts.csv` file containing the original contact information plus:
- Company Name
- Company Industry
- Company Revenue Range



## Rate Limiting

Please be aware of Surfe API's [rate limiting policies](https://developers.surfe.com/rate-limits) when running this script with large datasets.