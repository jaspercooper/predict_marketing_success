"""
Title: Fetch Data
Description: This script runs the different scripts that fetch data needed to do the analysis.
Author: Jasper Cooper
Usage:
    - Ensure the SAM_API_KEY is stored in a `.env` file in the root directory.
    - File paths are set in config.py
Notes:
    - API key is rate-limited to 10 requests per day.
    - Ensure that the "data/raw/" directory exists before running the script.
"""

from data_fetchers.fetch_firm_ueis import fetch_sam_data

fetch_sam_data()

