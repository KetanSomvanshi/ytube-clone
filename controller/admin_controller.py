import http

from fastapi import APIRouter, Depends, Path

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from models.ytube_model import AdminKeyInsertModel
from usecases.admin_usecase import AdminUseCase
from utils.utils import build_api_response

admin_router = APIRouter(prefix="/v1/admin", tags=["admin_router", "admin"])


@admin_router.post("/api-key", status_code=http.HTTPStatus.OK)
async def add_api_key(key_model: AdminKeyInsertModel, _=Depends(build_request_context)):
    """
    Update API key
    :param key_model: api_key: new API key
    :param _: build_request_context dependency injection handles the request context
    :return:
    """
    response: GenericResponseModel = AdminUseCase.add_api_keys(api_key=key_model.api_key)
    return build_api_response(response)


@admin_router.delete("/api-key/{api_key}", status_code=http.HTTPStatus.OK)
async def delete_api_key(_=Depends(build_request_context), api_key: str = Path(...)):
    """
    Delete API key
    :param _: build_request_context dependency injection handles the request context
    :param api_key: API key to delete
    :return:
    """
    response: GenericResponseModel = AdminUseCase.delete_api_keys(api_key=api_key)
    return build_api_response(response)
