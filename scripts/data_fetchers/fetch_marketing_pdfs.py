# Get file paths
from scripts.config import RAW_DATA_DIR
import requests
import re
import base64
# Import pathlib for path handling
from pathlib import Path

def fetch_raw_pdf_data(uei):
    """
    Downloads the base64 data needed to build the PDF embedded in the `gon.pdf_data` variable of a given page.

    Args:
        uei (str): The unique identifier for the capability page
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
        match = re.search(r'gon\.pdf_data\s*=\s*"([^"]+)"', response.text)
        if not match:
            raise ValueError(f"Could not find `gon.pdf_data` in the page for UEI {uei}.")

        pdf_data_base64 = match.group(1)

        print("Success!")
        # Return results as a dictionary including the uei, so that this can be used later
        return {"pdf_data_base64": pdf_data_base64, "uei": uei}
    except Exception as e:
        print(f"Error fetching data for UEI {uei} from {base_url}: {e}")

def extract_pdf_from_base64(fetched_base64_data):
    """
    This function converts the raw base64 string back into raw binary data and associates it with a UEI.

    Args:
        fetched_base64_data: This is a dictionary containing pdf_data_base_64 (str), the Base64-encoded PDF data, and uei (str), the Unique Entity Identifier for the PDF.

    Returns:
        dict: A dictionary containing the decoded PDF binary data and its UEI.
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
    This function converts the raw binary data into a pdf and outputs it to a file path.

    Args:
        binary_pdf_data (str): This is the string variable downloaded from the HTML file corresponding to the pdf
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


def fetch_capability_statement_pdfs(ueis):
    """
    This function is a wrapper for those above, that takes multiple UEIs and returns their pdfs

    Args:
        ueis (str): A list of UEIs
    """
    # loop through uei list
    for uei in ueis:
        # Get the raw data from html
        raw_base = fetch_raw_pdf_data(uei)
        # Convert it to binary
        raw_binary = extract_pdf_from_base64(raw_base)
        # Extract the binary to pdf
        output_pdf(raw_binary)