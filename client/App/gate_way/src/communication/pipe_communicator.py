import win32pipe
import win32file
import struct
import logging

DEFAULT_PIPE_NAME = "blocker_pipe"
DEFAULT_BYTES_TO_READ = 70000

class PipeCommunicator:
    """
    A class that communicates with the blocker using windows named pipes.

    Message Format To Blocker:
    {
        "code": <code>,
        "data": <dict>
    }
    """
    def __init__(self, pipe_name: str = DEFAULT_PIPE_NAME, buffer_size: int = DEFAULT_BYTES_TO_READ):
        """
        Initialize the communicator with the given pipe name and buffer size.

        Args:
            pipe_name (str): The name of the pipe to communicate with.
            buffer_size (int): The size of the buffer to use for communication.
        """
        self._pipe_name = fr"\\.\pipe\{pipe_name}"
        self._buffer_size = buffer_size
        self._pipe = None

        self._init_pipe()

    def _init_pipe(self) -> None:
        """
        Initialize the pipe.
        """
        try:
            self._pipe = win32pipe.CreateNamedPipe(
                self._pipe_name,
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                win32pipe.PIPE_UNLIMITED_INSTANCES,
                self._buffer_size,
                self._buffer_size,
                0,
                None
            )
        except Exception as e:
            logging.error(f"Failed to create pipe: {e}")
            raise

    def send_message(self, message: str) -> None:
        """
        Send a message to the pipe.

        Args:
            message (str): The message to send.
        """
        try:
            message_bytes = message.encode("utf-8")
            size_prefix = struct.pack("I", len(message_bytes))
            win32file.WriteFile(self._pipe, size_prefix + message_bytes)
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            raise

    def connect(self) -> None:
        """
        Connect to the pipe.
        """
        try:
            win32pipe.ConnectNamedPipe(self._pipe, None)
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

    def listen(self) -> str:
        """
        Listen for a message from the pipe.

        Returns:
            str: The message received from the pipe.
        """
        try:
            while self.is_pipe_connected():
                size_data = win32file.ReadFile(self._pipe, 4)[1]
                message_size = struct.unpack('I', size_data)[0]
                message = win32file.ReadFile(self._pipe, message_size)[1].decode("utf-8")
                print(message)
                if message == "exit":
                    return message
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
