from .communication.rest_communicator import RestCommunicator

BLOCKER_URL = "http://localhost:8000"

class UI_callables:
    def __init__(self):
        self._blocker_communicator = RestCommunicator(BLOCKER_URL)

    def filter_update(self, ads_filter: bool, adult_filter: bool) -> None:
        self._blocker_communicator.update_adult_ads(
            adult_ads=adult_filter, 
            ads_block=ads_filter
            )

    def add_domain(self, domain: str) -> None:
        self._blocker_communicator.add_domain(domain=domain)

    def remove_domain(self, domain: str) -> None:
        self._blocker_communicator.remove_domain(domain=domain)
