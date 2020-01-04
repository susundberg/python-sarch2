import logging

LOG = None
BASENAME = "supa"


class SarchException(Exception):
    pass



def setup_log(name):

    global LOG

    if LOG is None:
        logger = logging.getLogger(BASENAME)
        logger.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        fh = logging.FileHandler('/tmp/%s.log' % BASENAME, mode='a')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # add the handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        LOG = logger
    return logging.getLogger(BASENAME + "." + name)


class FileBase:

    def __init__(self):
        self.name = None
        self.size = None
        self.timestamp = None
        self.checksum = None

    def equals(self, other):
        for attr in ["name", "size", "timestamp", "checksum"]:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True
