from datetime import datetime, timezone
from typing import List

from config.constants import CacheKeys
from config.settings import GoogleIntegration
from controller.context_manager import context_log_meta, context_api_id
from data_adapter.redis import Cache
from data_adapter.ytube import YTubeVideoMeta
from integrations.google_api_integration import GoogleYoutubeIntegration
from logger import logger
from models.base import PaginationRequest, GenericResponseModel
from models.ytube_model import YTubeGetResponseModel, YTubeVideoInsertModel
from dateutil import parser

from utils.utils import ApiLockManager


class AdminUseCase:

    @staticmethod
    def add_api_keys(api_key: str) -> GenericResponseModel:
        """ admin can add api keys to keep rotating them """
        Cache.get_instance().sadd(CacheKeys.YOUTUBE_API_KEY, [api_key])
        return GenericResponseModel(message="Successfully added API key")

    @staticmethod
    def get_random_api_key() -> GenericResponseModel:
        """ admin can get a random api key to use """
        api_key = Cache.get_instance().srandmember(CacheKeys.YOUTUBE_API_KEY)
        #  if no api key is present in redis , use default key
        if not api_key:
            return GenericResponseModel(data=GoogleIntegration.api_key, message="No API key found , sending default")
        return GenericResponseModel(data=api_key, message="Successfully retrieved API key")

    @staticmethod
    def delete_api_keys(api_key: str) -> GenericResponseModel:
        """ admin can delete api keys """
        Cache.get_instance().srem(CacheKeys.YOUTUBE_API_KEY, [api_key])
        return GenericResponseModel(message="Successfully deleted API key")
