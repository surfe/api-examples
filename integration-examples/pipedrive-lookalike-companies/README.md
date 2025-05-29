# Pipedrive Lookalike Companies Integration

Find companies similar to your best customers using Surfe's company lookalike API. This integration analyzes your recently closed deals in Pipedrive, extracts company information, and finds similar companies to create as prospects in your pipeline.

## 🎯 What This Integration Does

1. **Analyzes Recent Wins**: Fetches recently closed (won) deals from your Pipedrive (last 30 days)
2. **Extracts Company Domains**: Identifies company domains from organization websites and person emails
3. **Finds Lookalikes**: Uses Surfe's AI to find up to 10 companies similar to your best customers
4. **Creates Basic Prospects**: Automatically creates prospect organizations and $5,000 deals in Pipedrive

## 🏢 Use Cases

- **Sales Team Prospecting**: Find companies similar to recent wins to improve conversion rates
- **Account-Based Marketing**: Identify targets that match your successful customer profile
- **Pipeline Development**: Quickly populate your pipeline with qualified prospects

## 📋 Prerequisites

- **Pipedrive Account**: With API access and recent closed deals
- **Surfe API Key**: With access to company lookalike functionality
- **Python 3.7+**: For running the integration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd integration-examples/pipedrive-lookalike-companies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file with your API credentials:

```bash
# Required API Keys
PIPEDRIVE_API_KEY=your_pipedrive_api_key_here
SURFE_API_KEY=your_surfe_api_key_here

# Optional Pipedrive Settings (for prospect targeting)
PIPEDRIVE_PIPELINE_ID=1                # Pipeline ID for new prospect deals
PIPEDRIVE_STAGE_ID=1                   # Stage ID for new prospect deals  
PIPEDRIVE_DEFAULT_OWNER_ID=123456      # Default owner for new prospects
```

### 3. Run the Integration

```bash
python main.py
```

## 🔧 Current Configuration

The integration uses these fixed settings:
- **Days Back**: 30 days (analyzes deals closed in last 30 days)
- **Max Lookalikes**: 10 companies (Surfe API limit)
- **Deal Value**: $5,000 per prospect (default value)

## 📊 Sample Output

```
🚀 Initializing services...
📊 Fetching recently closed deals from last 30 days...
✅ Found 12 recently closed deals

🔍 Extracting company domains from closed deals...
✅ Extracted 8 unique company domains
📋 Sample domains: acme-corp.com, techstartup.io, enterprise-solutions.com, globaldyn.com, nextgen.co

🎯 Searching for lookalike companies (max 10)...
✅ Found 8 lookalike companies

📝 Create these prospects in Pipedrive? (y/N): y

💼 Creating prospect organizations and deals in Pipedrive...
✅ Successfully created 8 prospects in Pipedrive

📊 INTEGRATION SUMMARY:
==================================================
Source deals analyzed: 12
Company domains extracted: 8
Lookalike companies found: 8
Prospects created in Pipedrive: 8
Total pipeline value: $40,000
Time period analyzed: Last 30 days
```

## 🔍 How It Works

### Step 1: Deal Analysis
- Fetches won deals from the last 30 days
- Extracts company domains from:
  - Organization website fields
  - Person email domains (excluding Gmail, Outlook, Yahoo, Hotmail)

### Step 2: Lookalike Discovery
- Sends company domains to Surfe's lookalike API
- Surfe returns up to 10 similar companies with:
  - Company names
  - Domains
  - Employee counts
  - Revenue estimates
  - Industry information
  - Similarity scores

### Step 3: User Confirmation
- Displays count of lookalike companies found
- Asks for user confirmation before creating prospects
- Allows user to skip prospect creation if desired

### Step 4: Basic Prospect Creation
- Creates organization records with company names only
- Checks for existing organizations to avoid duplicates
- Generates $5,000 prospect deals with descriptive titles
- Assigns to specified pipeline, stage, and owner (if configured)

## 🛠 API Integration Details

### Pipedrive API Usage
- **Deals Endpoint**: Fetches recent won deals with organization data
- **Organizations Endpoint**: Creates basic prospect companies (name only)
- **Organizations Search**: Prevents duplicate organization creation
- **Deals Endpoint**: Creates prospect deals

### Surfe API Usage
- **Company Lookalikes Endpoint** (`POST /v1/organizations/lookalikes`):
  ```json
  {
    "domains": ["customer1.com", "customer2.com"],
    "maxResults": 10
  }
  ```

## 🎮 Interactive Features

The script includes:
- **Progress Updates**: Real-time status of each step
- **Domain Display**: Shows sample extracted domains
- **User Confirmation**: Asks before creating prospects in Pipedrive
- **Comprehensive Summary**: Final report of all activities

## 📈 Business Impact

### Expected Outcomes
- **Faster Prospecting**: Automated discovery of similar companies
- **Better Targeting**: Companies similar to proven successful customers
- **Pipeline Growth**: Systematic addition of qualified prospects

### What You Get
- Basic prospect organizations in Pipedrive
- $5,000 deals for sales team follow-up
- Foundation for manual enrichment and outreach

## 🔄 Recommended Workflow

### Weekly/Monthly Execution
1. **Run Integration**: Execute script to find new lookalike prospects
2. **Review Prospects**: Sales team reviews newly created organizations
3. **Manual Enrichment**: Add website, industry, and contact information manually
4. **Begin Outreach**: Start prospecting activities on qualified targets

## 🚨 Current Limitations

- **Basic Data**: Only creates organization names and basic deals
- **No Custom Fields**: Website and industry information not automatically added
- **No Filtering**: All lookalike companies are created (no similarity filtering)
- **Fixed Configuration**: Days back (30) and max results (10) are hardcoded
- **Manual Enrichment Required**: Additional company details need manual entry

## 🔮 Future Enhancements

Potential improvements for future versions:
- Custom field creation for website and industry data
- Configurable similarity score filtering
- Priority scoring and ranking
- Detailed prospect display before creation
- Configurable time periods and result limits

## 🤝 Support

For issues with:
- **Pipedrive Integration**: Check API key permissions and recent deal data
- **Surfe Lookalikes**: Verify API key and v1 endpoint access
- **Script Errors**: Review environment variables and Python dependencies

## 📚 Related Examples

- [Pipedrive Contact Enrichment](../pipedrive-contact-enrichment/) - Enrich existing contacts
- [Company Enrichment](../company-enrichment-example/) - Basic company data enrichment
- [HubSpot Contact Enrichment](../hubspot-contact-enrichment/) - HubSpot alternative

---

**Note**: This is a basic implementation that creates simple prospect records. You can extend the functionality by adding custom fields, filtering, and advanced prospect scoring based on your specific needs. 