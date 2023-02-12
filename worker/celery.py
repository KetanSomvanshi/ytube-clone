import sys

from celery import Celery
from celery.signals import after_setup_logger

from config.settings import CELERY
from logger import logger as lg, logging

celery_app = Celery(
    'tasks',
    broker=CELERY.broker_uri,
    include=['worker.task_worker', 'worker.scheduler'], )


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    level = logging.DEBUG

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    logger.addHandler(handler)


class SQLAlchemyTask(celery_app.Task):
    """An abstract Celery Task that ensures that the connection of the database is closed on task completion
    Here we are using scoped_session for db connection, instead of creating session from get_db dependency injection"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        from controller.context_manager import remove_db_session, context_log_meta
        lg.info(extra=context_log_meta.get(),
                msg=f"Celery task completed with status {status} and task_id {task_id}")
        remove_db_session()
