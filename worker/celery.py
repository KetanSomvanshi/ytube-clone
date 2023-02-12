from celery import Celery
from celery.signals import setup_logging

import logger
from config.settings import CELERY
from logger import logger

celery_app = Celery(
    'tasks',
    broker=CELERY.broker_uri,
    include=['worker.task_worker', 'worker.scheduler'], )


@setup_logging.connect
def config_loggers(*args, **kwags):
    logger.info('Configuring loggers')
    logger_instance = logger.get_logger(__name__)
    logger_instance.info('Configuring loggers')


class SQLAlchemyTask(celery_app.Task):
    """An abstract Celery Task that ensures that the connection of the database is closed on task completion
    Here we are using scoped_session for db connection, instead of creating session from get_db dependency injection"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        from controller.context_manager import remove_db_session, context_log_meta
        logger.info(extra=context_log_meta.get(),
                    msg=f"Celery task completed with status {status} and task_id {task_id}")
        remove_db_session()
