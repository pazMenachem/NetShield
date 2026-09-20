from src.application import Application
from src.logger import setup_logger

def run() -> None:
    application = Application()
    application.run()

def main() -> None:
    try:
        run()
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        print("Application closed")

if __name__ == "__main__":
    main()