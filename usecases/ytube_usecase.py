from controller.context_manager import context_log_meta
from data_adapter.ytube import YTubeVideoMeta
from integrations.google_api_integration import GoogleYoutubeIntegration
from logger import logger
from models.base import PaginationRequest, GenericResponseModel
from models.ytube_model import YTubeGetResponseModel, YTubeVideoInsertModel


class YTubeUseCase:
    MSG_GET_VIDEOS_META_SUCCESS = "Successfully retrieved videos metadata"

    ERROR_GET_VIDEOS_META = "Error while retrieving videos metadata"

    @staticmethod
    def get_videos_metadata(paginator: PaginationRequest) -> GenericResponseModel:
        logger.info(extra=context_log_meta.get(), msg=f"get_videos_metadata: paginator: {paginator}")
        list_data = YTubeVideoMeta.list_ytube_videos_meta(paginator=paginator)
        response_data = YTubeGetResponseModel(data=list_data, pagination_data=paginator)
        if not response_data:
            logger.error(extra=context_log_meta.get(), msg=YTubeUseCase.ERROR_GET_VIDEOS_META)
            return GenericResponseModel(status_code=404, errors=YTubeUseCase.ERROR_GET_VIDEOS_META)
        return GenericResponseModel(data=list_data, message=YTubeUseCase.MSG_GET_VIDEOS_META_SUCCESS)

    @staticmethod
    def sync_videos_meta_from_external_system() -> GenericResponseModel:
        response: GenericResponseModel = GoogleYoutubeIntegration.sync_videos_meta_from_youtube()
        if response.errors:
            logger.error(extra=context_log_meta.get(),
                         msg=f"Error while syncing videos metadata from youtube: {response.errors}")
            return response
        try:
            models_to_insert_in_db = [YTubeVideoInsertModel.build_from_external_response(item) for item in
                                      response.data.get("items")]
            YTubeVideoMeta.insert_all(items=models_to_insert_in_db)
        except Exception as e:
            logger.error(extra=context_log_meta.get(), msg=f"Error while building models to insert in db: {e}")
            return GenericResponseModel(status_code=500, errors=str(e))
        logger.debug(extra=context_log_meta.get(),
                     msg=f"Successfully synced videos metadata from youtube: {response.data}")
