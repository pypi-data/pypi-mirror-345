import logging
import sys


# TODO set colors for each type of log
class Log:
    def __init__(self, name, level) -> None:
        logging.basicConfig(stream=sys.stdout)
        self.log = logging.getLogger(name)
        self.log.setLevel(level)  # logging.DEBUG)

    def info(self, text):
        self.log.info(text)

    def debug(self, text):
        self.log.debug(text)
