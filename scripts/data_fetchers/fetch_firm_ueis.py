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
# for data wrangling
import pandas as pd

# Set file paths
from scripts.config import RAW_DATA_DIR
from scripts.utils import comma_join

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
    print(f"Sending the following parameters to SAM API: {comma_join(params)}")
    # Send the GET request
    response = requests.get(base_url, params = params)
    # Check the response status
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(f"Successfully retrieved {data['totalRecords']} records")
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        print(response.text)
    # Output to raw data
    with open(f"{RAW_DATA_DIR}/raw_uei_data/sam_data.json", "w") as file:
        json.dump(data, file)
        print(f"Data saved to {RAW_DATA_DIR}/sam_data.json")

def read_sam_json(file_path = f"{RAW_DATA_DIR}/raw_uei_data/sam_data.json"):
    # Open the file and load the JSON data
    with open(file_path, "r") as file:
        data = json.load(file)
    # Print keys as a preview
    json_keys = data.keys()
    keys_to_print = comma_join(json_keys)
    print(f"JSON has the following keys: {keys_to_print}")
    return data

def square_and_clean_SAM_JSON(json_to_clean):
    entities = json_to_clean.get('entityData', [])
    print("Extracted entity data from JSON")
    df = pd.json_normalize(entities)
    print("Flattened JSON to df")
    clean_names = df.columns.str.replace(r'^.*\.', '', regex=True)
    df.columns = clean_names
    clean_names_to_print = comma_join(clean_names)
    print(f"Created a dataset with dimensions {df.shape} and the following keys: {clean_names_to_print}")
    return df



