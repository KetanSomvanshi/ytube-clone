import os
from logger import logger


class Environment:
    """Helper class to get environment variables"""

    @classmethod
    def get_string(cls, config_name, default=""):
        return str(os.getenv(config_name, default))

    @classmethod
    def get_int(cls, config_name, default=0):
        value = cls.get_string(config_name, str(default))
        try:
            value = int(eval(value))
        except(ValueError, TypeError, KeyError, EnvironmentError):
            logger.error("SERVER_INIT:CONFIG_ERROR::Invalid int value:{} for {}".format(value, config_name))
            return default
        return value

    @classmethod
    def get_bool(cls, config_name, default=False):
        value = cls.get_string(config_name, str(default))
        try:
            value = bool(eval(value))
        except(ValueError, TypeError, KeyError, EnvironmentError):
            logger.error("SERVER_INIT:CONFIG_ERROR::Invalid bool value:{} for {}".format(value, config_name))
            return default
        return value
