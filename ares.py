import os
import requests
import logging
import redis
import json

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional


logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

redis_host_name = os.environ.get("REDIS_HOST_NAME", "localhost")

try:
    redis_instance = redis.Redis(host=redis_host_name, port=6379, db=0)
except redis.RedisError as e:
    logging.error(f"Nepodařilo se připojit k Redisu: {e}")
    redis_instance = None


@dataclass
class AresCompany:
    ico: str
    name: Optional[str]
    address: Optional[str]
    psc: Optional[str]
    legal_form: Optional[str]
    business_fields: Optional[List[str]]
    size: Optional[str]
    main_cz_nace: Optional[str] = None
    based_main_cz_nace: Optional[str] = None


ATTRIBUTE_TAGS = {
    "name": "D:OF",
    "address": "D:UC",
    "psc": "D:PB",
    "legal_form": "D:NPF",
    "size": "D:KPP",
}


def get_soup(ico: str, ares_url: str) -> BeautifulSoup:
    response = requests.get(ares_url + str(ico))
    return BeautifulSoup(response.content, "lxml-xml")


def extract_data(soup: BeautifulSoup, tag: str) -> Optional[str]:
    found = soup.find(tag)
    return found.text if found else None


def extract_business_fields(soup: BeautifulSoup) -> Optional[AresCompany]:
    business_fields = soup.find_all("D:Obor_cinnosti")
    return (
        [field.find("D:T").text for field in business_fields if field.find("D:T")]
        if business_fields
        else None
    )


def get_company_data_ares(
    ico: str, ares_url: str = "http://wwwinfo.mfcr.cz/cgi-bin/ares/darv_bas.cgi?ico="
) -> Optional[AresCompany]:
    """
    Function to get company data from Ares using their ICO
    """
    url = ares_url + ico
    try:
        # Check if data already exists in cache
        if redis_instance is not None and redis_instance.exists(url):
            logging.info(f"Use cached data for {url}")
            data = json.loads(redis_instance.get(url))
            return AresCompany(**data)

        soup = get_soup(ico, ares_url)
        attributes = {
            attr: extract_data(soup, tag) for attr, tag in ATTRIBUTE_TAGS.items()
        }
        attributes["ico"] = ico
        attributes["business_fields"] = extract_business_fields(soup)
        company = AresCompany(**attributes)

        if redis_instance is not None:
            redis_instance.setex(url, 7 * 24 * 60 * 60, json.dumps(attributes)) # 7 day in cache

        return company

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get data from Ares for ICO: {ico}. Error: {e}")
        return None


def main():
    pass


if __name__ == "__main__":
    main()
