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


class GoogleIntegration:
    api_key = Environment.get_string("GOOGLE_API_KEY", "")
    videos_search_base_url = Environment.get_string("GOOGLE_VIDEOS_SEARCH_BASE_URL",
                                                    "https://www.googleapis.com/youtube/v3/search")
    max_results = Environment.get_int("GOOGLE_RESPONSE_MAX_RESULTS", 20)
    order = Environment.get_string("GOOGLE_REQUEST_ORDER", "date")
    type = Environment.get_string("GOOGLE_REQUEST_TYPE", "video")
    part = Environment.get_string("GOOGLE_REQUEST_PART", "snippet")
    query = Environment.get_string("GOOGLE_REQUEST_QUERY", "sports")
    published_after = Environment.get_string("GOOGLE_REQUEST_PUBLISHED_AFTER", "2021-02-01T00:00:00Z")


class CELERY:
    broker_uri = Environment.get_string("CELERY_BROKER_URI", "redis://localhost:6379/0")
    task_trigger_in_seconds = Environment.get_int("CELERY_TASK_TRIGGER_IN_SECONDS", 30)
