from src.communicator import Communicator
from src.block_manager import BlockManager
from src.block_settings_cache import BlockSettingsCache
import logging

def run():
    try:
        block_manager = BlockManager()
        block_manager.run()

    except Exception as e:
        logging.error(f"Blocker error: {e}")

def main():
    run()

if __name__ == "__main__":
    main()