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

from usecases.admin_usecase import AdminUseCase
from utils.utils import ApiLockManager


class YTubeUseCase:
    MSG_GET_VIDEOS_META_SUCCESS = "Successfully retrieved videos metadata"

    ERROR_GET_VIDEOS_META = "Error while retrieving videos metadata"

    @staticmethod
    def get_videos_metadata(paginator: PaginationRequest) -> GenericResponseModel:
        logger.info(extra=context_log_meta.get(), msg=f"get_videos_metadata: paginator: {paginator}")
        list_data = YTubeVideoMeta.list_ytube_videos_meta(paginator=paginator)
        response_data = YTubeGetResponseModel(data=list_data, pagination_data=paginator)
        response_data.pagination_data.total_count = YTubeUseCase.get_total_data_count()
        if not response_data:
            logger.error(extra=context_log_meta.get(), msg=YTubeUseCase.ERROR_GET_VIDEOS_META)
            return GenericResponseModel(status_code=404, errors=YTubeUseCase.ERROR_GET_VIDEOS_META)
        return GenericResponseModel(data=response_data, message=YTubeUseCase.MSG_GET_VIDEOS_META_SUCCESS)

    @staticmethod
    def sync_videos_meta_from_external_system() -> GenericResponseModel:
        """ Logic to sync videos from external system
        we would maintain a timestamp in redis max_published_at to fetch data after this timestamp
        min_published_at to fetch data before this timestamp , data within this range would be already synced
        """
        # There might be corner cases where syncs are triggered concurrently , we would use a lock to avoid that
        lock_manager: ApiLockManager = ApiLockManager(api_run_id=context_api_id.get())
        lock_acquired = lock_manager.acquire_lock_for_api()
        if not lock_acquired:
            logger.info(extra=context_log_meta.get(), msg="Sync already in progress , unable to acquire lock")
            return GenericResponseModel(status_code=200, message="Sync already in progress")
        try:
            max_published_at, min_published_at = YTubeUseCase.get_max_min_published_at()
            # get new key from redis else use default key if present
            youtube_api_key = AdminUseCase.get_random_api_key().data
            if not youtube_api_key:
                youtube_api_key = GoogleIntegration.api_key
            response: GenericResponseModel = GoogleYoutubeIntegration. \
                sync_videos_meta_from_youtube(api_key=youtube_api_key, max_published_at=max_published_at)
            if response.errors:
                logger.error(extra=context_log_meta.get(),
                             msg=f"Error while syncing videos metadata from youtube: {response.errors}")
                return response
            #  only items with published after max_published_at or before min_published_at timestamp would be required
            models_from_external_system: List[YTubeVideoInsertModel] = [
                YTubeVideoInsertModel.build_from_external_response(item) for item in response.data.get("items")
                if max_published_at < parser.parse(item.get('snippet').get('publishedAt')) < min_published_at]
            if not models_from_external_system:
                logger.info(extra=context_log_meta.get(),
                            msg=f"No new videos found from youtube with max_published_at: {max_published_at}"
                                f" and min_published_at: {min_published_at}")
                return GenericResponseModel(message="No new videos found from youtube")
            YTubeVideoMeta.insert_all(items=models_from_external_system)
            # increment total count in redis
            Cache.get_instance().increment(CacheKeys.TOTAL_DATA_COUNT, len(models_from_external_system))
            max_published_at = max(models_from_external_system[0].published_at, max_published_at)
            # to make sure redis cache is not filled with old data we should keep expiring the cache
            # after expired time we would fetch data from db and update the cache
            Cache.get_instance().set(key=CacheKeys.MAX_PUBLISH_AT, value=max_published_at.isoformat('T'),
                                     expiry_in_seconds=CacheKeys.EXPIRY)
            min_published_at = min(models_from_external_system[-1].published_at, min_published_at)
            Cache.get_instance().set(key=CacheKeys.MIN_PUBLISH_AT, value=min_published_at.isoformat('T'),
                                     expiry_in_seconds=CacheKeys.EXPIRY)
        except Exception as e:
            logger.error(extra=context_log_meta.get(), msg=f"Error while building models to insert in db: {e}")
            return GenericResponseModel(status_code=500, errors=str(e))
        finally:
            # release the lock before exit
            lock_manager.release_lock_for_api()
        logger.debug(extra=context_log_meta.get(),
                     msg=f"Successfully synced videos metadata from youtube: {response.data}")
        return GenericResponseModel(data=response.data, message="Successfully synced videos metadata from youtube")

    @staticmethod
    def get_max_min_published_at() -> (str, str):
        max_published_at = Cache.get_instance().get(key=CacheKeys.MAX_PUBLISH_AT)
        if not max_published_at:
            # if we do not have any max_published_at timestamp in redis we would get it form db
            max_published_at = YTubeVideoMeta.get_max_published_at()
            if not max_published_at:
                # if we do not have any max_published_at timestamp in db we would set it to initial_published_after
                max_published_at = GoogleIntegration.initial_published_after
            else:
                Cache.get_instance().set(key=CacheKeys.MAX_PUBLISH_AT, value=max_published_at.isoformat('T'),
                                         expiry_in_seconds=CacheKeys.EXPIRY)
        min_published_at = Cache.get_instance().get(key=CacheKeys.MIN_PUBLISH_AT)
        if not min_published_at:
            # if we do not have any min_published_at timestamp in redis we would get it form db
            min_published_at = YTubeVideoMeta.get_min_published_at()
            if not min_published_at:
                # if we do not have any min_published_at timestamp in db we would set it to now
                min_published_at = datetime.now(timezone.utc)
            else:
                Cache.get_instance().set(key=CacheKeys.MIN_PUBLISH_AT, value=min_published_at.isoformat('T'),
                                         expiry_in_seconds=CacheKeys.EXPIRY)
        if isinstance(max_published_at, str):
            max_published_at: datetime = parser.parse(max_published_at)
        if isinstance(min_published_at, str):
            min_published_at: datetime = parser.parse(min_published_at)
        return max_published_at, min_published_at

    @staticmethod
    def get_total_data_count() -> int:
        count = Cache.get_instance().get(key=CacheKeys.TOTAL_DATA_COUNT)
        if not count:
            count = YTubeVideoMeta.get_total_count()
            Cache.get_instance().set(key=CacheKeys.TOTAL_DATA_COUNT, value=count, expiry_in_seconds=CacheKeys.EXPIRY)
        return count

    @staticmethod
    def search_videos_meta_by_search_term(search_term: str, paginator: PaginationRequest) -> GenericResponseModel:
        logger.info(extra=context_log_meta.get(), msg=f"search_videos_meta_by_search_term: search_term: {search_term}")
        list_data, total_count = YTubeVideoMeta.search_videos_meta_by_search_term(search_term=search_term,
                                                                                  paginator=paginator)
        response_data = YTubeGetResponseModel(data=list_data, pagination_data=paginator)
        response_data.pagination_data.total_count = total_count
        if not response_data:
            logger.error(extra=context_log_meta.get(), msg=YTubeUseCase.ERROR_GET_VIDEOS_META)
            return GenericResponseModel(status_code=404, errors=YTubeUseCase.ERROR_GET_VIDEOS_META)
        return GenericResponseModel(data=response_data, message=YTubeUseCase.MSG_GET_VIDEOS_META_SUCCESS)
