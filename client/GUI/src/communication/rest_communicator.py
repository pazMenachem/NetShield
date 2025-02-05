import requests
from src.logger import setup_logger
import json
from .utils import *

class RestCommunicator:
    def __init__(self, url: str) -> None:
        self.logger = setup_logger(__name__)
        self._url = url

        self._actions = {
            ADD_DOMAIN_ROUTE: self.add_domain,
            REMOVE_DOMAIN_ROUTE: self.remove_domain,
            UPDATE_ADULT_ADS_ROUTE: self.update_adult_ads
        }

    def handle_request(self, request: str) -> None:
        request_dict = json.loads(request)

    def add_domain(self, domain: str) -> None:
        data = {
            DOMAINS: domain
        }
        requests.post(f"{self._url}{ADD_DOMAIN_ROUTE}", json=data)

    def remove_domain(self, domain: str) -> None:
        data = {
            DOMAINS: domain
        }
        requests.post(f"{self._url}{REMOVE_DOMAIN_ROUTE}", json=data)

    def update_adult_ads(self, adult_ads: bool, ads_block: bool) -> None:
        data = {
            ADULT_BLOCK: adult_ads,
            ADS_BLOCK: ads_block
        }
        requests.post(f"{self._url}{UPDATE_ADULT_ADS_ROUTE}", json=data)
