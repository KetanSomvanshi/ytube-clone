from typing import List

from sqlalchemy import Column, String, TIMESTAMP, Text, desc, func
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR
from sqlalchemy.orm import Session

from data_adapter.db import YTubeBase, DBBase
from models.base import PaginationRequest
from models.ytube_model import YTubeVideoMetaModel


class YTubeVideoMeta(DBBase, YTubeBase):
    __tablename__ = 'ytubemeta'

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    thumbnails = Column(JSON, nullable=True)
    published_at = Column(TIMESTAMP(timezone=True), nullable=False)
    channel_id = Column(String(255), nullable=True)
    channel_title = Column(String, nullable=True)
    # search_data is postgres tsvector column which is used for full text search
    #  we have a gin index on this column for faster search
    search_data = Column(TSVECTOR, nullable=True)

    def __to_model(self) -> YTubeVideoMetaModel:
        """converts db orm object to pydantic model"""
        return YTubeVideoMetaModel.from_orm(self)

    @classmethod
    def list_ytube_videos_meta(cls, paginator: PaginationRequest) -> List[YTubeVideoMetaModel]:
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        query = db.query(cls).filter(cls.is_deleted.is_(False))
        query = query.order_by(desc(cls.created_at)).limit(paginator.page_size).offset(
            paginator.page_size * paginator.page)
        return [obj.__to_model() for obj in query.all()]

    @classmethod
    def insert_all(cls, items: List[YTubeVideoMetaModel]):
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        db.bulk_save_objects([obj.build_db_model() for obj in items])
        db.flush()

    @classmethod
    def search_videos_meta_by_search_term(cls, search_term: str, paginator: PaginationRequest) -> \
            List[YTubeVideoMetaModel]:
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        query = db.query(cls).filter(cls.is_deleted.is_(False))
        # ts_query is a postgres function which converts a string to text search query
        #  we are using this function to convert search_term to ts_query
        # @@ is a postgres operator which is used to match ts_query with tsvector column
        query = query.filter(cls.search_data.op("@@")(func.plainto_tsquery(search_term))).limit(
            paginator.page_size).offset(paginator.page_size * paginator.page)
        return [obj.__to_model() for obj in query.all()]
