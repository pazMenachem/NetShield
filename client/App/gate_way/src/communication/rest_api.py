from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from .pipe_communicator import PipeCommunicator
from ..utils import *
import json
import uvicorn
from ..logger import setup_logger

UPDATE_ADULT_ADS_ROUTE = "/update_adult_ads"
INIT_BLOCKER_ROUTE     = "/init_blocker"
ADD_DOMAIN_ROUTE       = "/add_domain"
REMOVE_DOMAIN_ROUTE    = "/remove_domain"

DEFAULT_PORT = 8000

class RemoveDomainRequest(BaseModel):
    domains: str

class AddDomainRequest(BaseModel):
    domains: str

class UpdateAdultAdsRequest(BaseModel):
    adult_block: bool
    ads_block: bool

class InitBlockerRequest(BaseModel):
    adult_block: bool
    ads_block: bool
    domains: list[str]

class RestAPI:
    def __init__(self, port: int = DEFAULT_PORT):
        self._blocker_communicator = PipeCommunicator()
        self._app = FastAPI()
        self._logger = setup_logger(__name__)
        self._port = port

        self._setup()

    def start(self):
        try:
            self._logger.info("RestAPI started")
            uvicorn.run(self._app, host="0.0.0.0", port=self._port)
        except Exception as e:
            self._logger.error(f"RestAPI error: {e}")
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
            DOMAINS: request.domains
        }))
        return {STATUS: SUCCESS}

    async def _handle_remove_domain_request(self, request: RemoveDomainRequest):
        self._blocker_communicator.send_message(json.dumps({
            CODE: REMOVE_BLOCKED_DOMAIN,
            DOMAINS: request.domains
        }))
        return {STATUS: SUCCESS}
    async def _handle_update_adult_ads_request(self, request: UpdateAdultAdsRequest):
        self._blocker_communicator.send_message(json.dumps({
            CODE: UPDATE_ADULT_ADS,
            ADULT_BLOCK: request.adult_block,
            ADS_BLOCK: request.ads_block
        }))
        return {STATUS: SUCCESS}
    async def _handle_init_blocker_request(self, request: InitBlockerRequest):
        self._blocker_communicator.send_message(json.dumps({
            CODE: INIT_BLOCKER,
            ADULT_BLOCK: request.adult_block,
            ADS_BLOCK: request.ads_block,
            DOMAINS: request.domains
        }))
        return {STATUS: SUCCESS}
