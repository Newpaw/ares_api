
import os
import requests
import logging
import json

from conf import BRAND_FETCH_TOKEN

logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_company_data_by_domain(company_domain:str) -> dict | None:
    company_domain = company_domain.strip()
    url = f"https://api.brandfetch.io/v2/brands/{company_domain}"
    API_TOKEN = os.environ.get("BRAND_FETCH_TOKEN", BRAND_FETCH_TOKEN)

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # raise HTTPError if the HTTP request returned an unsuccessful status code

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

def get_logo_src(company_data):
    for logo in company_data['logos']:
        if logo['type'] == 'logo':
            for format in logo['formats']:
                return format['src']
    return None

def main():
    response = get_company_data_by_domain("mluvii.com")
    url = get_logo_src(response)
    print(url)


if __name__ == "__main__":
    main()