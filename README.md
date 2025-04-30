# Surfe API Integration Examples

This repository contains a collection of integration examples demonstrating how to use the Surfe API with various CRM and business tools. The examples are organized into the following structure:

## Repository Structure

```
surfe-apis/
├── core/                    # Shared code and utilities
│   ├── surfe/               # A service containing methods for calling different surfe APIs
│   ├── integrations/        # A directory containing several services for each platform's shared utils
│       ├── pipedrive/
│       ├── hubspot/
│
└── integration-examples/               # Individual integration examples
```

## Available Examples

### Contact Enrichment
- [Basic Contact Enrichment](integration-examples/contact-enrichment-example/) - Enrich contact information from CSV files
- [Pipedrive Contact Enrichment](integration-examples/pipedrive-contact-enrichment/) - Enrich contacts in Pipedrive
- [HubSpot Contact Enrichment](integration-examples/hubspot-contact-enrichment/) - Enrich contacts in HubSpot


### Company Enrichment
- [Company Enrichment](integration-examples/company-enrichment-example/) - Enrich company information from CSV files

### CRM Integrations
- [Intercom Priority](integration-examples/intercom-clevel-priority-example/) - Intercom priority level management

## Getting Started

1. Clone the repository
2. Start a virtual environment
3. Navigate to the example you want to run
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up your environment variables in a `.env` file following the `.env.example` file
6. Follow the project's README on how to run


