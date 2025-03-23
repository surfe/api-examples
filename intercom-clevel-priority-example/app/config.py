import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
INTERCOM_ACCESS_TOKEN = os.getenv("INTERCOM_ACCESS_TOKEN")
SURFE_API_KEY = os.getenv("SURFE_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Validate required environment variables
if not all([INTERCOM_ACCESS_TOKEN, SURFE_API_KEY, WEBHOOK_SECRET]):
    raise ValueError("Missing required environment variables")