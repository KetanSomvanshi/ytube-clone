from datetime import datetime
from typing import Optional, List

from pydantic.types import constr

from pydantic import BaseModel
from models.base import DBBaseModel, PaginationResponse


class YTubeVideoMetaModel(DBBaseModel):
    title: str = None
    description: str = None
    thumbnails: Optional[dict] = None
    published_at: datetime = None
    channel_id: Optional[constr(max_length=255)] = None
    channel_title: Optional[str] = None


class YTubeGetResponseModel(BaseModel):
    pagination_data: PaginationResponse
    data: List[YTubeVideoMetaModel]
