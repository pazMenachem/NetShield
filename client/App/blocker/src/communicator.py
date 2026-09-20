import win32pipe
import win32file
import struct
import logging
import json
from typing import Generator

class Communicator:
    """
    A class that provides a simple interface for communicating with GateWay component with a named pipe.

    Message Format:
    {
        "code": <int>,
        "data": <dict>
    }
    """
    def __init__(self, pipe_name: str):
        """
        Initialize the communicator with the given pipe name and buffer size.

        Args:
            pipe_name (str): The name of the pipe to communicate with.
            buffer_size (int): The size of the buffer to use for communication.
        """
        self._pipe_name = fr"\\.\pipe\{pipe_name}"
        self._pipe = None

    def send_message(self, message: str) -> None:
        """
        Send a message to the pipe.

        Args:
            message (str): The message to send.
        """
        try:
            message_bytes = message.encode("utf-8")
            size_prefix = struct.pack("I", len(message_bytes))
            self._pipe.WriteFile(size_prefix + message_bytes)
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            raise

    def connect(self) -> None:
        """
        Connect to the pipe.
        """
        try:
            self._pipe = win32file.CreateFile(
            self._pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE, 
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        except Exception as e:
            logging.error(f"Failed to connect to pipe: {e}")
            raise

    def is_pipe_connected(self) -> bool:
        """
        Check if the pipe is connected.

        Returns:
            bool: True if the pipe is connected, False otherwise.
        """
        try:
            win32pipe.PeekNamedPipe(self._pipe, 0)
            return True
        except Exception as e:
            logging.error(f"Connection to pipe lost: {e}")
            return False

    def listen(self) -> Generator[dict, None, None]:
        """
        Listen for a message from the pipe.

        Returns:
            Generator[dict, None, None]: The message received from the pipe.
        """
        try:
            while self.is_pipe_connected():
                size_data = win32file.ReadFile(self._pipe, 4)[1]
                message_size = struct.unpack('I', size_data)[0]
                message = win32file.ReadFile(self._pipe, message_size)[1].decode("utf-8")
                yield json.loads(message)

        except Exception as e:
            logging.error(f"Failed to listen: {e}")
            raise

    def cleanup(self) -> None:
        """
        Cleanup the pipe.
        """
        try:
            win32file.CloseHandle(self._pipe)
        except Exception as e:
            logging.error(f"Failed to close pipe: {e}")
            raise

    def __del__(self):
        self.cleanup()
