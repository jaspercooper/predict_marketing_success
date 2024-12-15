"""
Title: Fetch Award Data from USASpending.gov
Description: This script queries the USAspending API to get data on awards to 8(a) firms
Author: Jasper Cooper
Usage:
    - clarify
Notes:
    - notes here
"""

# Get file paths
from scripts.config import RAW_DATA_DIR
# Requests for API queries
import requests
# JSON for handling API queries
import json

def fetch_awards(ueis, year):
    # Initialize an empty list to store JSON responses
    successful_responses = []
    unsuccessful_responses = []

    # Base URL for the API
    base_url = "https://api.usaspending.gov/api/v2/recipient/children/"

    # Loop through each UEI and make a request
    for uei in ueis:
        # Construct the URL
        url = f"{base_url}{uei}/?year={year}"

        try:
            # Send GET request
            one_response = requests.get(url)

            # Check if the response is successful
            if one_response.status_code == 200:
                successful_responses.append(one_response.json())  # Append JSON response to the list
            else:
                unsuccessful_responses.append(one_response.json())
        except Exception as e:
            print(f"An error occurred for UEI {uei}: {e}")

    # Print the outcome
    print(f"Collected {len(successful_responses)} successful responses and {len(unsuccessful_responses)} unsuccessful responses.")

    save_location = f"{RAW_DATA_DIR}/raw_award_data/awards_to_8a_{year}.json"
    with open(save_location, "w") as file:
        json.dump(successful_responses, file)
        print(f"successful_responses saved to {save_location}")