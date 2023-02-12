from typing import Optional, Any

from pydantic.main import BaseModel
from datetime import datetime

from pydantic.types import constr


class GenericResponseModel(BaseModel):
    """Generic response model for all responses"""
    api_id: Optional[str] = None
    errors: Optional[str]
    message: Optional[str]
    data: Any
    status_code: Optional[int] = None


class DBBaseModel(BaseModel):
    """Base model for all models that will be stored in the database"""
    id: int
    external_id: constr(min_length=1, max_length=255)
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool

    class Config:
        orm_mode = True


class PaginationRequest(BaseModel):
    """Basic Pagination request model , can be reused for any pagination request"""
    """Pagination request model alternatively provides last_timestamp as well which can be used by clients
    in fast moving data , using page number as offset might not be a good idea as data might have changed after
    last fetch , so we can use last_timestamp to fetch data after that timestamp provided by client"""
    page: Optional[int] = 0
    page_size: Optional[int] = 20
    last_timestamp: Optional[datetime] = None


class PaginationResponse(PaginationRequest):
    """Basic Pagination response model , can be reused for any pagination response"""
    total_count: Optional[int] = 0
