import logging

class Logger():
    def __init__(self, name):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(name)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warn(self, msg):
        self.logger.warn(msg)
