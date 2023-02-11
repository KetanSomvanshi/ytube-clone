from controller.context_manager import context_log_meta
from logger import logger
from models.base import GenericResponseModel
from worker.celery import celery_app, SQLAlchemyTask
from usecases.ytube_usecase import YTubeUseCase


@celery_app.task(base=SQLAlchemyTask)
def trigger_yt_video_metadata_sync():
    """ This is a celery task which is triggered by scheduler to sync videos metadata from youtube
    Internally this would call the usecase as usecase has business logic to sync videos metadata from youtube
    command to run worker - 'celery -A worker.task_worker worker -B' """
    response: GenericResponseModel = YTubeUseCase().sync_videos_meta_from_external_system()
    if response.errors:
        logger.error(extra=context_log_meta.get(),
                     msg=f"Error while syncing videos metadata from youtube: {response.errors}")
        return response
    logger.debug(extra=context_log_meta.get(),
                 msg=f"Successfully synced videos metadata from youtube: {response.data}")
