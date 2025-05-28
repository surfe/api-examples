import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

account_id = os.getenv("ZOOM_ACCOUNT_ID")
client_id = os.getenv("ZOOM_CLIENT_ID") 
client_secret = os.getenv("ZOOM_CLIENT_SECRET")

# Encode credentials
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Request token

url = f"https://zoom.us/oauth/token"
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "grant_type": "account_credentials",
    "account_id": account_id
}

response = requests.post(url, headers=headers, data=data)
token_data = response.json()
access_token = token_data.get("access_token")

print(f"ZOOM_API_TOKEN={access_token}")