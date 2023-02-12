from contextvars import ContextVar

import uuid
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from data_adapter.db import get_db, db_session
from logger import logger

# we are using context variables to store request level context , as FASTAPI
# does not provide request context out of the box
context_db_session: ContextVar[Session] = ContextVar('db_session', default=None)
context_api_id: ContextVar[str] = ContextVar('api_id')
context_log_meta: ContextVar[dict] = ContextVar('log_meta', default={})


def clear_context():
    """method to clear context , to be used by worker"""
    context_db_session.set(None)
    context_api_id.set(None)
    context_log_meta.set({})


async def build_request_context(request: Request,
                                db: Session = Depends(get_db)):
    # set the db-session in context-var so that we don't have to pass this dependency downstream
    context_db_session.set(db)
    context_api_id.set(str(uuid.uuid4()))
    context_log_meta.set({'api_id': context_api_id.get(), 'request_id': request.headers.get('X-Request-ID')})
    logger.info(extra={"api_id": context_api_id.get()}, msg="REQUEST_INITIATED")


def build_non_request_context():
    """method to build context for non-request context , to be used by worker"""
    # clear past context first
    clear_context()
    context_api_id.set(str(uuid.uuid4()))
    context_log_meta.set({'api_id': context_api_id.get()})


def get_db_session() -> Session:
    """only this function should be used for session creation for any type of request
    if session is already present in context_var then context_db_session would be returned
    all rest APIs have get_db dependency injected which puts db_session in context var context_db_session
    for non-rest requests(requests on worker) context_db_session is None , here we can create scoped session
    (check for scoped session creation in db.py) and return it.

    every session initiates a default transaction and this transaction should be either committed or rolled back
    before session is closed.
    we use default setting of sqlalchemy autocommit = False.

    Make sure each session is closed at the end of request processing
    for rest api requests get_db takes care of closing the session in finally and for non-rest api requests use
    db_session.remove() to close the session"""
    db = context_db_session.get()
    if db:
        return db
    return db_session


def remove_db_session(rollback=False):
    db = get_db_session()
    if rollback:
        db.rollback()
    else:
        db.commit()
    db.close()
