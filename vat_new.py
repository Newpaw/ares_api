import requests
from dataclasses import dataclass

@dataclass
class Company:
    isValid: bool = None
    requestDate: str = None
    userError: str = None
    name: str = None
    address: str = None
    vatNumber: str = None


class VatInfo:
    def __init__(self, vat_input: str):
        self.base_url = 'https://pexpats.com/api/v1/util-functions/get-vat-info'
        self.country = vat_input[:2]
        self.vat_number = vat_input[2:]

    def get_vat_info(self):
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
            # Extract only the needed properties
            properties = data.get('properties', {})
            address = properties.get('address')
            # Replace newline characters with a space
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
            return company
        else:
            return None


