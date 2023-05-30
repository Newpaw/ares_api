import os
import requests
import json
import redis
import logging

from dataclasses import dataclass, field
from bs4 import BeautifulSoup



logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

redis_host_name = os.environ.get("REDIS_HOST_NAME", "localhost")


def default_headers():
    return {
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    }

@dataclass
class CompanyByVAT:
    vat_id: str
    url: str = "https://www.iban.com/vat-checker"
    headers: dict = field(default_factory=default_headers)
    redis_db: redis.Redis = field(default_factory=lambda: redis.Redis(host='localhost', port=6379, db=0))

    def get_company_info(self):
        data = {'vat_id': self.vat_id}
        response = requests.post(self.url, headers=self.headers, data=data)
        return response.text

    @staticmethod
    def parse_company_info(html):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', attrs={'class': 'table table-bordered downloads'})
        rows = table.find_all('tr')

        company_info = {}
        for row in rows[1:]:
            cells = row.find_all('td')
            company_info[cells[0].text.strip()] = cells[1].text.strip()

        return company_info

    def cache_company_info(self, company_info):
        # Uložení výsledků do Redisu
        self.redis_db.setex(self.vat_id, 30 * 24 * 60 * 60, json.dumps(company_info)) # 30 days in cache

    def get_cached_company_info(self):
        # Pokus o získání informací ze serveru Redis
        cached_info = self.redis_db.get(self.vat_id)
        if cached_info:
            return json.loads(cached_info)
        else:
            return None

def main():
    pass



if __name__=='__main__':
    main()