from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from blocker_communicator import BlockerCommunicator
from utils import *
import json
import uvicorn
from logger import setup_logger

UPDATE_ADULT_ADS_ROUTE = "/update_adult_ads"
INIT_BLOCKER_ROUTE     = "/init_blocker"
ADD_DOMAIN_ROUTE       = "/add_domain"
REMOVE_DOMAIN_ROUTE    = "/remove_domain"

class RemoveDomainRequest(BaseModel):
    domain: str

class AddDomainRequest(BaseModel):
    domain: str

class UpdateAdultAdsRequest(BaseModel):
    adult_block: bool
    ads_block: bool

class InitBlockerRequest(BaseModel):
    adult_block: bool
    ads_block: bool
    domains: list[str]

class RestCommunicator:
    def __init__(self):
        self._blocker_communicator = BlockerCommunicator()
        self._app = FastAPI()
        self._logger = setup_logger("RestCommunicator")

        self._setup()

    def start(self):
        try:
            uvicorn.run(self._app, host="0.0.0.0", port=8000)
            self._logger.info("RestCommunicator started")
        except Exception as e:
            self._logger.error(f"RestCommunicator error: {e}")
            raise e
    
    def _setup(self):
        # Routes
        self._app.post(ADD_DOMAIN_ROUTE)(self._handle_add_domain_request)
        self._app.post(REMOVE_DOMAIN_ROUTE)(self._handle_remove_domain_request)
        self._app.post(UPDATE_ADULT_ADS_ROUTE)(self._handle_update_adult_ads_request)
        self._app.post(INIT_BLOCKER_ROUTE)(self._handle_init_blocker_request)
        
        # Other
        self._blocker_communicator.connect()
    
    async def _handle_add_domain_request(self, request: AddDomainRequest):
        self._blocker_communicator.send_message(json.dumps({
            CODE: ADD_BLOCKED_DOMAIN,
            DATA: {
                DOMAINS: request.domain
            }
        }))

    async def _handle_remove_domain_request(self, request: RemoveDomainRequest):
        self._blocker_communicator.send_message(json.dumps({
            CODE: REMOVE_BLOCKED_DOMAIN,
            DATA: {
                DOMAINS: request.domain
            }
        }))

    async def _handle_update_adult_ads_request(self, request: UpdateAdultAdsRequest):
        self._blocker_communicator.send_message(json.dumps({
            CODE: UPDATE_ADULT_ADS,
            DATA: {
                ADULT_BLOCK: request.adult_block,
                ADS_BLOCK: request.ads_block
            }
        }))
    
    async def _handle_init_blocker_request(self, request: InitBlockerRequest):
        self._blocker_communicator.send_message(json.dumps({
            CODE: INIT_BLOCKER,
            DATA: {
                ADULT_BLOCK: request.adult_block,
                ADS_BLOCK: request.ads_block,
                DOMAINS: request.domains
            }
        }))
