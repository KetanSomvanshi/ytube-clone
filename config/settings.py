from dotenv import load_dotenv

from config.util import Environment
from logger import logger

# Load env variables from a file, if exists
logger.info("SERVER_INIT::Setting environment variables from .env file(if exists)...")
load_dotenv(verbose=True)


class AUTH:
    user = Environment.get_string("AUTH_USER", "")
    pass_ = Environment.get_string("AUTH_PASS", "")
