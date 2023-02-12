from datetime import datetime

from config.settings import GoogleIntegration
from controller.context_manager import context_log_meta
from logger import logger
from models.base import GenericResponseModel
from models.ytube_model import GoogleApiParams
from utils.utils import make_request


class GoogleYoutubeIntegration:

    @staticmethod
    def sync_videos_meta_from_youtube(api_key, max_published_at: datetime = GoogleIntegration.initial_published_after) \
            -> GenericResponseModel:
        """ Sync videos metadata from youtube apis
        :param max_published_at: datetime , we only fetch data after this timestamp"""
        if not max_published_at:
            max_published_at = GoogleIntegration.initial_published_after
        else:
            max_published_at = max_published_at.isoformat('T')
        request_params = GoogleApiParams(key=api_key, part=GoogleIntegration.part,
                                         order=GoogleIntegration.order,
                                         type=GoogleIntegration.type, max_results=GoogleIntegration.max_results,
                                         q=GoogleIntegration.query,
                                         publishedAfter=max_published_at)
        response_data, status_code = make_request(external_service_url=GoogleIntegration.videos_search_base_url,
                                                  request_params=request_params.dict())
        if status_code != 200:
            logger.error(extra=context_log_meta.get(),
                         msg=f"Error while syncing videos metadata from youtube: {response_data}"
                             f" with status_code: {status_code}")
            return GenericResponseModel(status_code=status_code)
        logger.info(extra=context_log_meta.get(),
                    msg=f"Successfully synced videos metadata from youtube: {response_data}"
                        f" with status_code: {status_code} data : {response_data}")
        return GenericResponseModel(data=response_data, message="Successfully synced videos metadata from youtube")
