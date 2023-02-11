import logging
import sys


def get_logger(name, level=logging.DEBUG) -> logging.Logger:
    FORMAT = "[%(levelname)s  %(name)s %(module)s:%(lineno)s - %(funcName)s() - %(asctime)s]\n\t %(message)s \n"
    TIME_FORMAT = "%d.%m.%Y %I:%M:%S %p"
    FILENAME = './log.log'
    logging.basicConfig(format=FORMAT, datefmt=TIME_FORMAT, level=level, filename=FILENAME)

    logger_instance = logging.getLogger(name)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    logger_instance.addHandler(handler)
    return logger_instance


logger = get_logger(__name__)

logger.info(f'Logger initiated')
