# Intercom C-Level Priority Example

This example demonstrates how to automatically set priority levels for Intercom conversations based on the contact's seniority level using the Surfe API.

## Overview

The application is a FastAPI service that:
1. Receives webhooks from Intercom for new conversations
2. Identifies the contact's seniority level using Surfe API
3. Automatically sets priority tags for conversations with C-level executives


## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows use: env\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   INTERCOM_ACCESS_TOKEN=your_intercom_token
   SURFE_API_KEY=your_surfe_api_key
   WEBHOOK_SECRET=your_webhook_secret
   ```

## Usage

1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
2. For local development, expose your webhook using ngrok:
   ```bash
   	ngrok http 8000
   ```
2. Configure Intercom webhook:
   - Go to Intercom settings
   - Add a new webhook
   - Set the URL to: `https://your-ngrok-url/webhook/intercom`
   - Select the event: `conversation.user.created`
   - Save the webhook

## Priority Rules

The system automatically sets priority tags for conversations when:
- The contact is identified as C-level executive
- The contact belongs to the C-suite department

## API Endpoints

### Webhook Endpoint
- `POST /webhook/intercom`: Receives Intercom webhooks
- `HEAD /webhook/intercom`: Handles webhook validation

## Requirements

- Python 3.6+
- FastAPI
- Intercom API key
- Surfe API key
- Intercom Webhook secret

## Rate Limiting

Both Intercom and Surfe APIs have rate limits. The application includes built-in rate limit handling, but you should be aware of:
- Intercom API limits: [Intercom API Docs](https://developers.intercom.com/docs)
- Surfe API limits: [Surfe API Limits](https://developers.surfe.com/rate-limits)
