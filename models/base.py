from typing import Optional, Any

from pydantic.main import BaseModel
from datetime import datetime

from pydantic.types import constr


class GenericResponseModel(BaseModel):
    api_id: Optional[str] = None
    errors: Optional[str]
    message: Optional[str]
    data: Any
    status_code: Optional[int] = None


class DBBaseModel(BaseModel):
    id: int
    external_id: constr(min_length=1, max_length=255)
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool

    class Config:
        orm_mode = True


class PaginationRequest(BaseModel):
    page: Optional[int] = 0
    page_size: Optional[int] = 20
    last_timestamp: Optional[datetime] = None


class PaginationResponse(PaginationRequest):
    total_count: Optional[int] = 0
