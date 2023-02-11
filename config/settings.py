from dotenv import load_dotenv

from config.util import Environment
from logger import logger

# Load env variables from a file, if exists else default would be set
logger.info("SERVER_INIT::Setting environment variables from .env file(if exists)...")
load_dotenv(verbose=True)


class AUTH:
    user = Environment.get_string("AUTH", "user")
    pass_ = Environment.get_string("PASS", "pass")


class DB:
    host = Environment.get_string("DB_HOST", "localhost")
    port = Environment.get_string("DB_PORT", '5432')
    name = Environment.get_string("DB_NAME", "test")
    user = Environment.get_string("DB_USER", "")
    pass_ = Environment.get_string("DB_PASS", "")
