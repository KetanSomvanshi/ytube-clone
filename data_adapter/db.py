from datetime import datetime
from urllib.parse import quote_plus

from pytz import timezone
from sqlalchemy import Column, TIMESTAMP, Boolean, Integer, create_engine, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.orm import sessionmaker

from config.settings import DB
from logger import logging

DBTYPE_POSTGRES = 'postgresql'
CORE_SQLALCHEMY_DATABASE_URI = '%s://%s:%s@%s:%s/%s' % (
    DBTYPE_POSTGRES, DB.user, quote_plus(DB.pass_), DB.host, DB.port, DB.name)

db_engine = create_engine(CORE_SQLALCHEMY_DATABASE_URI)

logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

# scoped_session should be strictly used where it is guaranteed that there would be use of single thread local like....
# .....in the case of celery
# but in cases of async stuff thread locals is not mapped to a single request , single request in fastapi can use.....
# ..... multiple thread locals or single thread local can handle multiple requests
# Also make sure you explicitly do db_session.remove() on teardown of the thread local
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db_engine))

UTC = timezone('UTC')


def time_now():
    return datetime.now(UTC)


DBBase = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        # to be executed when request closes
        db.commit()
        db.close()


# base class for all database objects
class YTubeBase:
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    external_id = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=time_now, onupdate=time_now, nullable=False)
    is_deleted = Column(Boolean, default=False)
