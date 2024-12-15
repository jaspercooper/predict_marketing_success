"""
Title: Fetch Firm UEIs from SAM.gov
Description: This script queries the SAM.gov API to retrieve UEIs for active 8(a)-certified firms
             and saves the results in JSON format.
Author: Jasper Cooper
Usage:
    - Ensure the SAM_API_KEY is stored in a `.env` file in the root directory.
    - File paths are set in config.py
Notes:
    - API key is rate-limited to 10 requests per day.
    - Ensure that the "data/raw/" directory exists before running the script.
"""

# for API queries
import requests
# for handling JSON
import json
# for getting API key from .env
import os
# Set file paths
from code.config import RAW_DATA_DIR
# Get API key
sam_api_key = os.environ.get("SAM_API_KEY")
# Base URL for the API
base_url = "https://api.sam.gov/entity-information/v2/entities"

def fetch_sam_data(base_url = "https://api.sam.gov/entity-information/v2/entities", sam_api_key = sam_api_key):
    # Parameters for the API query
    params = {
        "api_key": sam_api_key,
        # Filtering for SBA 8(a)-certified firms
        "sbaBusinessTypeCode": "A6",
        # Active registration status
        "registrationStatus": "A"
    }

    # Send the GET request
    response = requests.get(base_url, params = params)

    # Check the response status
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(data)
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        print(response.text)
    # Output to raw data
    with open(f"{RAW_DATA_DIR}/raw_uei_data/sam_data_test.json", "w") as file:
        json.dump(data, file)

    print("Data saved to sam_data.json")

