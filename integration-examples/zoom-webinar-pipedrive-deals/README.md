# Zoom Webinar Lead Generation with Pipedrive Deals Integration

This integration example demonstrates how to:
1. Fetch webinar registrants from Zoom API
2. Process registrants to extract name and company information
3. Enrich leads with Surfe API (emails, phone numbers, job titles, etc.)
4. Calculate lead scores based on enriched data
5. Create persons and deals in Pipedrive with automatic value assignment
6. Assign deals to sales reps based on territory/department logic
7. Create follow-up activities for immediate sales action

## Key Features

### 🎯 **Lead Scoring Algorithm**
- Job title scoring (CEO/Founder: 30pts, VP/Director: 25pts, Manager: 20pts)
- Seniority level scoring (C-Level: 25pts, VP: 20pts, Director: 15pts)
- Department scoring (Executive/Finance: 15pts, Sales/Marketing: 12pts)
- Email validation scoring (Valid email: 10pts)
- Phone number availability (5pts)

### 💰 **Dynamic Deal Valuation**
- Base value: $5,000
- C-Level multiplier: 3x ($15,000)
- VP-Level multiplier: 2.5x ($12,500)
- Director multiplier: 2x ($10,000)
- Manager multiplier: 1.5x ($7,500)
- Enterprise webinar topics: +50% bonus

### 🎯 **Territory Assignment**
- Automatic deal assignment based on prospect's department
- Customizable territory mapping
- Fallback to default owner

### 📋 **Automated Follow-up**
- Creates scheduled activities for each deal
- Includes lead score and enriched data in activity notes
- Sets due date for next business day

## Prerequisites

- Zoom API credentials (Server-to-Server OAuth recommended)
- Surfe API key
- Pipedrive API key
- A Zoom webinar ID with registrants
- Pipedrive pipeline and stage IDs configured
- Pipedrive user IDs for deal assignment

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

```bash
# Zoom Configuration
ZOOM_API_TOKEN=your_zoom_server_to_server_token
ZOOM_WEBINAR_ID=1234567890

# Surfe Configuration
SURFE_API_KEY=your_surfe_api_key

# Pipedrive Configuration
PIPEDRIVE_API_KEY=your_pipedrive_api_key
PIPEDRIVE_PIPELINE_ID=1
PIPEDRIVE_STAGE_ID=1  # "Webinar Lead" stage ID
PIPEDRIVE_DEFAULT_OWNER_ID=1234567  # Default sales rep user ID
```

## Usage

Run the script to execute the full workflow:

```bash
python main.py
```

## Sample Output

```
Fetching registrants for webinar 1234567890...
Found 8 registrants for the webinar

Processing registrants to extract name and company information...
Found 6 registrants with valid name and company information

Preparing Surfe enrichment...
Starting Surfe enrichment process...
Enrichment started with ID: enrich_abc123

Polling for enrichment results...
Enrichment completed successfully
Enriched 6 registrants

Creating persons and deals in Pipedrive...

Creating person for John Smith...
Created person with ID: 12345
Creating deal for John Smith (Score: 85, Value: $15,000)...
Created deal with ID: 67890
Created follow-up activity with ID: 11111

Person Sarah Johnson already exists with ID: 12346
Creating deal for Sarah Johnson (Score: 70, Value: $10,000)...
Created deal with ID: 67891
Created follow-up activity with ID: 11112

Skipping Michael Brown - Low lead score (25)

Creating person for Emily Davis...
Created person with ID: 12347
Creating deal for Emily Davis (Score: 60, Value: $7,500)...
Created deal with ID: 67892
Created follow-up activity with ID: 11113

=== INTEGRATION SUMMARY ===
Successfully processed 3 webinar attendees
Total pipeline value created: $32,500
Average deal value: $10,833
Webinar: Advanced Sales Strategies for Enterprise Growth
Pipeline ID: 1
Stage: Webinar Lead
```

## Flow Overview

1. **Fetch Registrants**: Script retrieves all registrants from specified Zoom webinar
2. **Data Processing**: Filters registrants with complete name and company information
3. **Surfe Enrichment**: Enriches contact data with emails, phone numbers, job titles, and company details
4. **Lead Scoring**: Calculates lead quality score (0-100) based on enriched data
5. **Quality Filter**: Skips leads with scores below 30 to focus on high-quality prospects
6. **Deal Valuation**: Determines deal value based on seniority and webinar topic
7. **Person Management**: Creates new persons or updates existing ones in Pipedrive
8. **Deal Creation**: Creates deals with calculated values and assigns to appropriate sales reps
9. **Activity Scheduling**: Creates follow-up activities with enriched context
10. **Reporting**: Provides summary of pipeline value created and success metrics

## Customization Options

### Lead Scoring
Modify the `calculate_lead_score()` function to adjust scoring criteria:
- Change point values for different job titles
- Add industry-specific scoring
- Include company size factors
- Add geographic scoring

### Deal Valuation
Customize the `determine_deal_value()` function to:
- Adjust base values for your business
- Add industry-specific multipliers
- Include company size factors
- Add seasonal adjustments

### Territory Assignment
Update the `assign_deal_owner()` function to:
- Add geographic territory mapping
- Include industry-based assignment
- Add round-robin assignment logic
- Include workload balancing

### Custom Fields
Add custom fields to deals by modifying the `deal_data` dictionary:
```python
"custom_fields": {
    "lead_score": lead_score,
    "lead_source": "Zoom Webinar",
    "webinar_topic": webinar_topic,
    "industry": enriched_person.get("industry"),
    "company_size": enriched_person.get("companySize"),
    "geographic_region": determine_region(enriched_person)
}
```

## Integration Benefits

### vs. Manual Process
- **Time Savings**: Automates 2-3 hours of manual data entry per webinar
- **Data Quality**: Ensures consistent, enriched contact information
- **Lead Scoring**: Objective qualification based on multiple data points
- **No Missed Opportunities**: Immediate follow-up scheduling

### vs. Basic Email Sequences
- **CRM Integration**: Full pipeline visibility and reporting
- **Deal Tracking**: Revenue forecasting and conversion metrics
- **Territory Management**: Proper lead distribution
- **Activity Management**: Structured follow-up process

### Sales Team Benefits
- **Qualified Leads**: Only high-scoring prospects enter pipeline
- **Rich Context**: Detailed prospect information for personalized outreach
- **Automatic Assignment**: Leads routed to appropriate sales reps
- **Immediate Action**: Follow-up activities scheduled automatically

## Notes

- The script handles pagination for Zoom API endpoints automatically
- Registrants without sufficient data for enrichment are filtered out
- Lead scoring threshold can be adjusted based on your qualification criteria
- Deal values and territory assignments are fully customizable
- Error handling ensures individual failures don't stop the entire process
- Duplicate detection prevents creating multiple persons for the same email 