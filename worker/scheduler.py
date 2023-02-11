from config.settings import CELERY
from worker.celery import celery_app

from worker.task_worker import trigger_yt_video_metadata_sync


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """This scheduler would periodically trigger the assigned task
    command to run scheduler - 'celery -A worker.scheduler beat' """
    sender.add_periodic_task(CELERY.task_trigger_in_seconds, trigger_yt_video_metadata_sync,
                             name='trigger sync every x seconds')
