import json
import threading
from src.view import Viewer
from src.logger import setup_logger

# from .rest_communicator.rest_communicator import RestCommunicator

# from .rest_communicator.utils import (
#     STR_DOMAINS, STR_OPERATION,
#     Codes
# )

class Application:
    def __init__(self) -> None:
        """Initialize application components."""
        self._logger = setup_logger(__name__)
        
        self._view = Viewer()

    def run(self) -> None:        
        self._start_gui()

    def _start_gui(self) -> None:
        """Start the GUI main loop."""
        try:
            self._view.run()
            
        except Exception as e:
            self._logger.error(e)
            raise

    # def _handle_user_input(self, request: str) -> None:
    #     """
    #     Handle outgoing messages from the UI and Server.
        
    #     Args:
    #         request: received request from server or user input from UI.
    #     """
    #     try:
    #         self._logger.info(f"Processing request: {request}")
    #         request_dict = json.loads(request)
            
                        
    #     except json.JSONDecodeError as e:
    #         self._logger.error(f"Invalid JSON format: {str(e)}")
    #         raise
    #     except Exception as e:
    #         self._logger.error(f"Error handling request: {str(e)}")
    #         raise

    # def __del__(self) -> None:
    #     """Clean up resources and stop threads."""
    #     self._logger.info("Cleaning up application resources")
    #     try:
    #         # if self._communicator:
    #         #     self._communicator.close()
                
    #         # if self._view and self._view.root.winfo_exists():
    #         #     self._view.root.destroy()
                
    #     except Exception as e:
    #         self._logger.warning(f"Cleanup encountered an error: {str(e)}")

    def _start_communication(self) -> None:
        """Initialize and start the communication thread."""
        try:
            threading.Thread(
                target=self._communicator.receive_message,
                daemon=True
            ).start()
            
            self._logger.info("Communication server started successfully")
        except Exception as e:
            self._logger.error(f"Failed to start communication: {str(e)}")
            raise