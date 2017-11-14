import logging
import logging.handlers


class Log():

    def __init__(self, logger):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        LOG_FILE = 'debug.log'
        handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE,when = 'D', interval=1, backupCount = 40)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.addHandler(ch)

    def getlog(self):
        return self.logger
