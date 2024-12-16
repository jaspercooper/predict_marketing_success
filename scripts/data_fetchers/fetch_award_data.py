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
# Get utility functions
from scripts.utils import subset_string, comma_join
# Requests for API queries
import requests
# JSON for handling API queries
import json
# For date handling:
import datetime
# For navigating OS
import os
# for dataframes
import pandas as pd

def fetch_awards(ueis, year, save_unsuccessful = False):
    """
    Fetches award data for a list of UEIs for a given year using the USAspending API.

    Parameters:
        ueis (list): A list of Unique Entity Identifiers (UEIs). Must not be empty.
        year (int): The year for which data is to be fetched. Must be a valid year.
        save_unsuccessful (bool): Whether to save unsuccessful responses to a file. Default is False.

    Returns:
        None: Saves successful responses to a JSON file.
    """

    # Validate parameters
    if not isinstance(ueis, (list, pd.Series)) or not ueis:
        raise ValueError("The 'ueis' parameter must be a non-empty list or pandas Series.")

    if not isinstance(year, int) or not year:
        raise ValueError("`year` must be a valid integer representing a year (e.g., 2023).")

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

    # Optionally save unsuccessful responses
    if save_unsuccessful:
        error_save_location = f"{RAW_DATA_DIR}/raw_award_data/unsuccessful_award_fetch_{year}.json"
        with open(error_save_location, "w") as file:
            json.dump(unsuccessful_responses, file, indent=4)
            print(f"Unsuccessful responses saved to {error_save_location}")


def concatenate_json_files(input_dir):
    """
    Reads all JSON files in the specified directory, concatenates their data into a single DataFrame,
    and includes the year extracted from the filenames.

    Parameters:
        input_dir (str): The directory containing JSON files.

    Returns:
        pd.DataFrame: A concatenated DataFrame containing all the data.
    """
    # Get list of files downloaded using fetch_awards()
    award_jsons = os.listdir(input_dir)
    json_names = subset_string(string_list=award_jsons, substring="awards_to_8a")

    # Initialize an empty list to store DataFrames
    all_dfs = []

    # Loop through all files in the input directory
    for file_name in json_names:
        # Check if the file has a .json extension
        if file_name.endswith(".json"):
            file_path = os.path.join(input_dir, file_name)

            # Extract year from the filename (assuming the format includes the year)
            try:
                year = int(file_name.split("_")[-1].split(".")[0])  # Extract year from "awards_to_8a_YEAR.json"
            except ValueError:
                print(f"Unable to extract year from filename: {file_name}")
                continue

            # Open and read the JSON file
            with open(file_path, "r") as file:
                try:
                    data = json.load(file)

                    # Flatten the data into a DataFrame
                    flat_data = [item for sublist in data for item in sublist]
                    df = pd.DataFrame(flat_data)

                    # Add the year as a new column
                    df['year'] = year

                    # Append the DataFrame to the list
                    all_dfs.append(df)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {file_name}")

    # Concatenate all DataFrames into one
    final_df = pd.concat(all_dfs, ignore_index=True)

    return final_df
