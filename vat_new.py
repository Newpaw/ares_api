import os
import requests
import json
import redis
import logging

from dataclasses import dataclass, asdict


logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def default_headers():
    return {
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    }



@dataclass
class Company:
    isValid: bool = None
    requestDate: str = None
    userError: str = None
    name: str = None
    address: str = None
    vatNumber: str = None


redis_host_name = os.environ.get("REDIS_HOST_NAME", "localhost")

@dataclass
class VatInfo:
    vat_input: str
    base_url: str = 'https://pexpats.com/api/v1/util-functions/get-vat-info'

    def __post_init__(self):
        self.country = self.vat_input[:2]
        self.vat_number = self.vat_input[2:]
        self.redis_db = redis.Redis(host=redis_host_name, port=6379, db=0)

    def get_vat_info(self):
        redis_key = f'vat_info:{self.country}:{self.vat_number}'
        cached_data = self.redis_db.get(redis_key)
        
        if cached_data is not None:
            logging.info("Used cache data!")
            return Company(**json.loads(cached_data))

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        }
        params = {
            'country': self.country,
            'vatNumber': self.vat_number
        }
        response = requests.get(self.base_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', {})
            address = properties.get('address')
            if address is not None:
                address = address.replace('\n', ' ')
            company = Company(
                isValid=properties.get('isValid'),
                requestDate=properties.get('requestDate'),
                userError=properties.get('userError'),
                name=properties.get('name'),
                address=address,
                vatNumber=properties.get('vatNumber')
            )

            if company.isValid:
                self.redis_db.setex(redis_key, 7 * 24 * 60 * 60, json.dumps(asdict(company)))
                return company

            return company

        return None


def main():
    pass



if __name__ == "__main__":
    main()