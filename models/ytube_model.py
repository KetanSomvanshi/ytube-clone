from datetime import datetime
from typing import Optional, List

from pydantic.types import constr

from pydantic import BaseModel

from models.base import DBBaseModel, PaginationResponse


class YTubeVideoInsertModel(BaseModel):
    """Pydantic model for inserting a video"""
    title: str = None
    description: str = None
    thumbnails: Optional[dict] = None
    published_at: datetime = None
    channel_id: Optional[constr(max_length=255)] = None
    channel_title: Optional[str] = None
    external_id: constr(min_length=1, max_length=255) = None

    @classmethod
    def build_from_external_response(cls, external_item_response):
        return cls(
            title=external_item_response.get('snippet').get('title'),
            description=external_item_response.get('snippet').get('description'),
            thumbnails=external_item_response.get('snippet').get('thumbnails'),
            published_at=external_item_response.get('snippet').get('publishedAt'),
            channel_id=external_item_response.get('snippet').get('channelId'),
            channel_title=external_item_response.get('snippet').get('channelTitle'),
            external_id=external_item_response.get('id').get('videoId')
        )

    def build_db_model(self):
        from data_adapter.ytube import YTubeVideoMeta
        return YTubeVideoMeta(**self.dict())


class YTubeVideoMetaModel(DBBaseModel, YTubeVideoInsertModel):
    """Pydantic equivalent model of orm model"""
    pass


class YTubeGetResponseModel(BaseModel):
    """Pydantic model for response of get request"""
    pagination_data: PaginationResponse
    data: List[YTubeVideoMetaModel]


class GoogleApiParams(BaseModel):
    """"Pydantic model for google youtube api request params"""
    key: str = None
    part: Optional[str] = 'snippet'
    maxResults: Optional[int] = 20
    order: Optional[str] = 'date'
    type: Optional[str] = 'video'
    q: Optional[str] = ''
    publishedAfter: Optional[str] = None

    def dict(self, **kwargs):
        return super().dict(**kwargs, exclude_none=True)


class AdminKeyInsertModel(BaseModel):
    api_key: str = None
