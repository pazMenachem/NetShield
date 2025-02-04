import win32api
import win32serviceutil
import win32service
import win32event
import servicemanager
import logging
from communication.rest_api import RestAPI
import time
import json
from src.utils import *

# class SimpleService(win32serviceutil.ServiceFramework):
#     """Basic Windows Service"""
    
#     _svc_name_ = "Blocking Gateway"
#     _svc_display_name_ = "I'm not a packet blocker"

#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.stop_event = win32event.CreateEvent(None, 0, 0, None)

#     def SvcStop(self):
#         """Handle service stop request"""
#         win32event.SetEvent(self.stop_event)

#     def SvcDoRun(self):
#         """Main service logic"""
#         try:
#             logging.info("Blocking Service starting...")

#         except Exception as e:
#             logging.error(f"Service error: {str(e)}")

#     def SvcShutdown(self):
#         """Handle system shutdown"""
#         self.SvcStop()
    
#     def cleanup(self):
#         """Cleanup resources"""
#         try:
#             # Close the event handle
#             if self.stop_event:
#                 win32api.CloseHandle(self.stop_event)
                
#             # Add any other cleanup code here
#             logging.info("Service cleanup completed")
            
#         except Exception as e:
#             logging.error(f"Cleanup error: {str(e)}")
def run():
    rest_api = RestAPI()
    rest_api.start()

def main():
    try:
        run()
    except Exception as e:
        logging.error(f"Main error: {e}")
    finally:
        logging.info("Gateway shutting down")

if __name__ == "__main__":
    main()
    # win32serviceutil.HandleCommandLine(SimpleService)