from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv('KITE_API_KEY')
print(f"Using API Key: {api_key}")

# Your access token here
access_token = "YOUR_ACCESS_TOKEN_HERE"  # Replace this with your token

try:
    # Initialize KiteConnect
    kite = KiteConnect(api_key=api_key)
    print("KiteConnect initialized")
    
    # Set the access token
    kite.set_access_token(access_token)
    print("Access token set")
    
    # Try to get profile
    profile = kite.profile()
    print("Success! Profile data:", profile)
    
except Exception as e:
    print(f"Error: {str(e)}")
