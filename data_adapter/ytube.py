from typing import List

from sqlalchemy import Column, String, TIMESTAMP, Text, desc
from sqlalchemy.dialects.postgresql import JSON
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
