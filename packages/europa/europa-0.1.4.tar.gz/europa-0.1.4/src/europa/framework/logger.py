import logging

class Logger:
    """
    A wrapper class for logging to allow easy replacement with other logging mechanisms.
    """

    def __init__(self, name: str):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s] %(message)s")
        self._logger = logging.getLogger(name)

    def debug(self, message: str):
        self._logger.debug(message)

    def info(self, message: str):
        self._logger.info(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def critical(self, message: str):
        self._logger.critical(message)