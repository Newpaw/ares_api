import os
import requests
import logging
import json
import glob
import cairosvg

from typing import Dict, Optional

import importlib

# check if the module exists
spec = importlib.util.find_spec("conf")
if spec is not None:
    # the module exists, import it
    from conf import BRAND_FETCH_TOKEN
else:
    # the module does not exist, do something else
    BRAND_FETCH_TOKEN = None
    logging.warning("No BRAND_FETCH_TOKEN.")

logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_company_data_from_brandfetch_by_domain(company_domain:str) -> Dict:
    """
    Get company data from Brandfetch API by given domain.

    Parameters:
    company_domain (str): Domain of the company.

    Returns:
    dict|None: Return dictionary with company data if the request is successful, None otherwise.
    """
    company_domain = company_domain.strip()
    url = f"https://api.brandfetch.io/v2/brands/{company_domain}"
    API_TOKEN = os.environ.get("BRAND_FETCH_TOKEN", BRAND_FETCH_TOKEN)

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        # Try to convert the response to JSON
        json_response = response.json()
        logging.info(f"Request for company domain {company_domain} is OK!")
        return json_response

    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")

    except requests.exceptions.ConnectionError as err:
        logging.error(f"Connection error occurred: {err}")

    except json.JSONDecodeError:
        logging.error("Failed to parse response to JSON.")

    except requests.exceptions.RequestException as err:
        logging.error(f"Other requests exception occurred: {err}")


def get_logo_src(company_data:dict, logo_type:str ='logo'):
    """
    Get the source URL of a logo from company data.

    Parameters:
    company_data (dict): Company data containing logos.
    logo_type (str): Type of the logo to retrieve. Default is 'logo'.

    Returns:
    str|None: Return the source URL of the logo if exists, None otherwise.
    """

    if company_data is not None:
        try:
            for logo in company_data['logos']:
                if logo['type'] == logo_type:
                    for format in logo['formats']:
                        return format['src']
        except TypeError as err:
            logging.error(f"The company with this domain doesnt exist: {err}")

    return None


def is_url_image(url:str) -> bool:
    """
    Check if the url is an image.

    Parameters:
    url (str): URL to check.

    Returns:
    bool: Return True if the URL points to an image, False otherwise.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()  
        content_type = response.headers.get('content-type')
        
        if 'image' in content_type.lower():
            return True
        else:
            logging.error(f"URL is not an image: {url}")
            return False

    except requests.exceptions.RequestException as err:
        logging.error(f"Request exception occurred: {err}")
        return False


def download_image(url:str):
    """
    Download an image from the given URL.

    Parameters:
    url (str): URL of the image to download.

    Returns:
    bytes|None: Return the image data if the request is successful, None otherwise.
    """

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as err:
        logging.error(f"Request exception occurred: {err}")
        return None


def save_image(data:bytes, file_path:str):
    """
    Save image data to a file.

    Parameters:
    data (bytes): Image data to save.
    file_path (str): Path where the image will be saved.
    """

    with open(file_path, 'wb') as file:
        file.write(data)
    logging.info(f"Image was saved: {file_path}")


def get_logo(domain:str):
    """
    Get logo.

    Parameters:
    domain (str): Domain in string without http:// or https:// 
    """
    directory = os.path.join(os.getcwd(), domain)  # get current working directory and domain as folder

    if os.path.exists(directory):
        logging.info(f"Directory '{directory}' already exists. Skipping download.")
        return

    response = get_company_data_from_brandfetch_by_domain(domain)
    url = get_logo_src(response)
    if is_url_image(url):
        image_data = download_image(url)
        if image_data is not None:
            os.makedirs(domain, exist_ok=True)
            filename = url.split("/")[-1]
            file_path = os.path.join(domain, filename)
            save_image(image_data, file_path)

def get_logo_path(domain):
    files = glob.glob(f"{domain}/*")
    img_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg'))]

    if img_files:
        return img_files[0]
    logging.info(f"No image file with domain {domain} found.")
    return None

def get_media_type(file_path: str) -> Optional[str]:
    extension = os.path.splitext(file_path)[1].lower()
    media_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.svg': 'image/svg+xml'
    }
    return media_types.get(extension)


def convert_svg_to_png(file_path: str) -> str:
    png_file_path = os.path.splitext(file_path)[0] + '.png'
    cairosvg.svg2png(url=file_path, write_to=png_file_path)
    return png_file_path

def main():
    pass

if __name__ == "__main__":
    main()
