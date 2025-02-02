from threading import Lock
from src.logger import setup_logger
from src.utils import *
import netifaces

# DNS servers
AD_GUARD        = "94.140.14.14"   # For ads block
AD_GUARD_FAMILY = "94.140.14.0/24" # For ads/Adult block
CLOUD_FLARE     = "1.1.1.3"        # For adult block

class BlockSettingsCache:
    def __init__(self, fixed_size: int = 256):
        self._block_list         = set()
        self._fixed_size         = fixed_size
        self._adult_block        = False
        self._ads_block          = False
        self._lock               = Lock()
        self._gateway_ip         = self._get_default_gateway()
        self._current_dns_server = self._gateway_ip
        self._logger             = setup_logger("BlockSettingsCache")
        self._dns_server_map     = {
            (True, False): CLOUD_FLARE,     # Adult only
            (False, True): AD_GUARD,        # Ads only
            (True, True): AD_GUARD_FAMILY,  # Both
            (False, False): self._gateway_ip  # Neither
        }

    def add_block(self, block: str) -> str | None:
        with self._lock:
            if len(self._block_list) <= self._fixed_size:
                self._logger.info(f"Adding block: {block}")
                self._block_list.add(block)
                return block
            return None

    def remove_block(self, block: str) -> str | None:
        with self._lock:
            if block in self._block_list:
                self._block_list.remove(block)
                return block
            return None

    def get_block_list(self) -> list[str]:
        with self._lock:
            return list(self._block_list)
    
    def is_blocked(self, domain: str) -> bool:
        with self._lock:
            return domain in self._block_list
    
    def update_adult_ads_settings(self, adult_block: bool, ads_block: bool):
        with self._lock:
            self._adult_block = adult_block
            self._ads_block = ads_block
            self._current_dns_server = self._dns_server_map[(adult_block, ads_block)]

    def get_adult_ads_settings(self) -> dict:
        with self._lock:
            return {
                "ADULT_BLOCK": self._adult_block,
                "ADS_BLOCK": self._ads_block
            }

    def get_block_settings(self) -> dict:
        with self._lock:
            return {
                DOMAINS: self._block_list,
                ADULT_BLOCK: self._adult_block,
                ADS_BLOCK: self._ads_block
            }

    def get_dns_server(self) -> str:
        with self._lock:
            return self._current_dns_server

    def get_gateway_ip(self) -> str:
        return self._gateway_ip

    def _get_default_gateway(self) -> str | None:
        """
        Get the default gateway (router) IP address.
        
        Returns:
            str: The default gateway IP address if found
            None: If gateway cannot be determined
        """
        try:
            return netifaces.gateways()['default'][netifaces.AF_INET][0]
        except Exception as e:
            self._logger.error(f"Gateway not found: {e}")
            return None