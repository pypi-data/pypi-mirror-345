import threading
import time
from websocket import create_connection


class ThreadedWebSocketClient:
    def __init__(self, websocket_url, message_handler=None, opening_message = None):
        """
        Initialize the WebSocket client.

        :param websocket_url: The WebSocket server URL to connect to.
        :param message_handler: A callback function to handle incoming messages.
        """
        self.websocket_url = websocket_url
        self.message_handler = message_handler
        self.opening_message = opening_message
        self.thread = None
        self._running = False
        self.ws = None  # Store the WebSocket connection

    def start(self):
        """
        Start the WebSocket client in a separate thread.
        """
        self._running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Stop the WebSocket client.
        """
        self._running = False
        if self.thread:
            self.thread.join()
        if self.ws:
            self.ws.close()

    def _run(self):
        """
        Connect to the WebSocket server and listen for messages.
        """
        while self._running:
            try:
                self.ws = create_connection(self.websocket_url)
                print(f"Connected to WebSocket: {self.websocket_url}")

                if self.opening_message:
                    self.send_message(self.opening_message)

                while self._running:
                    message = self.ws.recv()
                    if message:
                        self._handle_message(message)

            except Exception as e:
                print(f"WebSocket error: {e}")
                time.sleep(5)  # Reconnect after a delay

    def _handle_message(self, message):
        """
        Handle incoming WebSocket messages.

        :param message: The received WebSocket message.
        """
        if self.message_handler:
            self.message_handler(message)
        else:
            print(f"Received WebSocket message: {message}")

    def send_message(self, message):
        """
        Send a message through the WebSocket connection.

        :param message: The message to send.
        """
        if self.ws:
            try:
                self.ws.send(message)
                print(f"Sent message: {message}")
            except Exception as e:
                print(f"Failed to send message: {e}")
        else:
            print("WebSocket connection is not established.")
