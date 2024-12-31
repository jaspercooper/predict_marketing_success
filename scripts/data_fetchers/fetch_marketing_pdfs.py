import requests
import re
import base64
from pathlib import Path
import os

# Import RAW_DATA_DIR from config
from scripts.config import RAW_DATA_DIR

def fetch_raw_pdf_data(uei):
    """
    Fetches the Base64 data needed to build the PDF embedded in the `gon.pdf_data` variable of a given page.

    Args:
        uei (str): The unique identifier for the capability page.

    Returns:
        dict: A dictionary containing:
            - pdf_data_base64 (str): The Base64-encoded PDF data or a message indicating no data is available.
            - uei (str): The unique identifier for the PDF.
    """
    base_url = f"https://certify.sba.gov/capabilities/{uei}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    try:
        print(f"Fetching data from {base_url}...")
        # Fetch the page HTML
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        # Extract `gon.pdf_data` using regex
        match = re.search(pattern=r'gon\.pdf_data\s*=\s*"([^"]+)"', string = response.text)
        if not match:
            no_statement = re.search(pattern= 'No Capability Statement uploaded for UEI', string = response.text)
            if no_statement:
                return({"pdf_data_base64": f"No Capability Statement uploaded for UEI {uei}", "uei": uei})
            else:
                raise ValueError(f"Could not find `gon.pdf_data` in the page for UEI {uei}.")

        pdf_data_base64 = match.group(1)

        print("Success!")
        # Return results as a dictionary including the uei, so that this can be used later
        return {"pdf_data_base64": pdf_data_base64, "uei": uei}
    except Exception as e:
        print(f"Error fetching data for UEI {uei} from {base_url}: {e}")
        return None

def extract_pdf_from_base64(fetched_base64_data):
    """
    Decodes the raw Base64 string into binary data and retains the UEI for reference.

    Args:
        fetched_base64_data (dict): Contains:
            - pdf_data_base64 (str): The Base64-encoded PDF data.
            - uei (str): The Unique Entity Identifier for the PDF.

    Returns:
        dict: A dictionary containing:
            - pdf_data (bytes): The decoded binary PDF data.
            - uei (str): The unique identifier for the PDF.
    """
    # Extract relevant objects from the dictionary
    pdf_data_base_64 = fetched_base64_data["pdf_data_base64"]
    uei = fetched_base64_data["uei"]
    print(f"Extracting binary data for UEI {uei}")
    try:
        # Decode Base64 PDF data
        pdf_data = base64.b64decode(pdf_data_base_64)
        # Again, the UEI is carried through in the dictionary so it can be
        # used later
        print("Success!")
        return {"pdf_data": pdf_data, "uei": uei}
    except Exception as e:
        print(f"Error processing the base64 string for UEI {uei}: {e}")
        return None

def output_pdf(binary_pdf_data, output_dir = f"{RAW_DATA_DIR}/raw_pdfs/"):
    """
    Saves the binary PDF data to a file.

    Args:
        binary_pdf_data (dict): Contains:
            - pdf_data (bytes): The binary PDF data.
            - uei (str): The unique identifier for the PDF.
        output_dir (str): The directory where PDFs will be saved.
    """
    pdf_data = binary_pdf_data["pdf_data"]
    uei = binary_pdf_data["uei"]
    output_path = Path(output_dir) / f"{uei}.pdf"
    print(f"Creating PDF at {output_path}")
    try:
        # Save the PDF
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Create directory if needed
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(pdf_data)

        print(f"PDF successfully saved: {output_path}")
    except Exception as e:
        print(f"Error outputting PDF for UEI {uei}: {e}")
        return None


# need to add two types of debugging:
# Firstly, should not loop through PDFs that have already been downloaded.
# Secondly, should have error handling for when no cap statement exists

def fetch_capability_statement_pdfs(ueis, output_dir = f"{RAW_DATA_DIR}/raw_pdfs/"):
    """
    Saves the binary PDF data to a file.

    Args:
        binary_pdf_data (dict): Contains:
            - pdf_data (bytes): The binary PDF data.
            - uei (str): The unique identifier for the PDF.
        output_dir (str): The directory where PDFs will be saved.
    """
    # First check that we are only downloading pdfs that haven't already been downloaded

    # Get list of downloaded pdfs
    downloaded_pdfs_raw = os.listdir(output_dir)
    # Remove .pdf extension to get uei
    downloaded_pdfs = [filename.replace('.pdf', '') for filename in downloaded_pdfs_raw]
    # Use comprehension to create list of UEIs that are not in the downloaded PDFs list
    ueis_to_download = [uei for uei in ueis if uei not in downloaded_pdfs]

    # loop through list of UEIs to download
    for uei in ueis_to_download:
        # Get the raw data from html
        raw_base = fetch_raw_pdf_data(uei)
        # Check if there is no statement
        no_statement = re.search(pattern='No Capability Statement uploaded for UEI', string=raw_base["pdf_data_base64"])
        if no_statement:
            print(raw_base["pdf_data_base64"])
        else:
            # Convert it to binary
            raw_binary = extract_pdf_from_base64(raw_base)
            # Extract the binary to pdf
            output_pdf(raw_binary)