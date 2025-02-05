from abc import ABC, abstractmethod
from typing import Dict, Union
from src.utils import *
from src.block_settings_cache import BlockSettingsCache
from src.logger import setup_logger

"""
 *** Handler Interface ***
"""
class IHandler(ABC):
    """Abstract base interface for domain blocking handlers."""
    
    def __init__(self, block_settings_cache: BlockSettingsCache) -> None:
        self._block_settings_cache = block_settings_cache
        self._logger = setup_logger(name=__name__)

    @abstractmethod
    def handle_request(self) -> None:
        """Handle the request operation. Must be implemented by subclasses."""
        pass

"""
 *** Handlers ***
"""
class AddBlockedDomainHandler(IHandler):
    def __init__(self, data: Dict[str, str], block_settings_cache: BlockSettingsCache) -> None:
        super().__init__(block_settings_cache)
        self._domain: str = data[DOMAINS]
    
    def handle_request(self) -> None:
        self._block_settings_cache.add_block(block=self._domain)

class RemoveBlockedDomainHandler(IHandler):
    def __init__(self, data: Dict[str, str], block_settings_cache: BlockSettingsCache) -> None:
        super().__init__(block_settings_cache)
        self._domain = data[DOMAINS]

    def handle_request(self) -> None:
        self._block_settings_cache.remove_block(block=self._domain)

class UpdateAdultAdsHandler(IHandler):
    def __init__(self, data: Dict[str, bool], block_settings_cache: BlockSettingsCache) -> None:
        super().__init__(block_settings_cache)
        self._adult_block = data[ADULT_BLOCK]
        self._ads_block = data[ADS_BLOCK]

    def handle_request(self) -> None:
        self._block_settings_cache.update_adult_ads_settings(
            adult_block=self._adult_block,
            ads_block=self._ads_block
        )

class InitBlockerHandler(IHandler):
    def __init__(self, data: Dict[str, Union[str, bool]], block_settings_cache: BlockSettingsCache) -> None:
        super().__init__(block_settings_cache)
        self._domains     = data[DOMAINS].split(",")
        self._adult_block = data[ADULT_BLOCK]
        self._ads_block   = data[ADS_BLOCK]

    def handle_request(self) -> None:
        for domain in self._domains:
            self._block_settings_cache.add_block(block=domain)
        self._block_settings_cache.update_adult_ads_settings(
            adult_block=self._adult_block,
            ads_block=self._ads_block
        )

## Will implement once the blocker will send messages, at the moment he's only receiving them
class GetBlockSettingsHandler(IHandler):
    def __init__(self, block_settings_cache: BlockSettingsCache, data: Dict[str, str] = None) -> None:
        super().__init__(block_settings_cache)

    def handle_request(self) -> None:
        self._logger.info(f"Getting domains and settings: {self._block_settings_cache.get_block_settings()}")
"""
 *** Handler Factory ***
"""
class HandlerFactory:
    """Factory class for creating domain blocking handlers."""

    def __init__(self):
        self._logger = setup_logger(name="HandlerFactory")
        self._handlers = {
            ADD_BLOCKED_DOMAIN   : AddBlockedDomainHandler,
            REMOVE_BLOCKED_DOMAIN: RemoveBlockedDomainHandler,
            UPDATE_ADULT_ADS     : UpdateAdultAdsHandler,
            INIT_BLOCKER         : InitBlockerHandler,
            GET_BLOCK_SETTINGS   : GetBlockSettingsHandler
        }

    def get_handler(self, data: Dict[str, Union[str, bool]], 
                   block_settings_cache: BlockSettingsCache) -> IHandler:
        """
        Get the handler for the given code.

        Args:
            data (Dict[str, Union[str, bool]]): The data to be handled.
            block_settings_cache (BlockSettingsCache): The block settings cache.

        Returns:
            IHandler: The handler for the given code.
        """
        self._logger.info(f"Processing request: {data}")
        code = data[CODE]
        handler_class = self._handlers.get(code)
        self._logger.info(f"Processing request: {handler_class}")

        if handler_class is None:
            self._logger.error(f"Invalid code: {code}")
            raise ValueError(f"Invalid code: {code}")
        try:
            return handler_class(data=data, block_settings_cache=block_settings_cache)
        except KeyError as e:
            self._logger.error(f"Missing 'CODE' field: {e}")
        except Exception as e:
            self._logger.error(f"Error initializing handler: {e}")
