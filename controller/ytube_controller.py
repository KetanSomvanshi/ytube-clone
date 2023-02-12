import http

from fastapi import APIRouter, Depends, Query

from controller.context_manager import build_request_context
from models.base import GenericResponseModel, PaginationRequest
from usecases.ytube_usecase import YTubeUseCase
from utils.utils import build_api_response

video_router = APIRouter(prefix="/v1/video", tags=["video_router", "video"])


@video_router.get("", status_code=http.HTTPStatus.OK)
async def get_videos_metadata(_=Depends(build_request_context), paginator: PaginationRequest = Depends()):
    """
    Get videos metadata in paginated format
    :param _: build_request_context dependency injection handles the request context
    :param paginator: basic pagination request
    :return:
    """
    response: GenericResponseModel = YTubeUseCase.get_videos_metadata(paginator=paginator)
    return build_api_response(response)


@video_router.get("/search", status_code=http.HTTPStatus.OK)
async def get_videos_metadata(_=Depends(build_request_context), paginator: PaginationRequest = Depends(),
                              search_term: str = Query(...)):
    """
    Get videos metadata in paginated format
    :param _: build_request_context dependency injection handles the request context
    :param paginator: basic pagination request.
    :param search_term: search term to filter videos
    :return:
    """
    response: GenericResponseModel = YTubeUseCase.search_videos_meta_by_search_term(search_term=search_term,
                                                                                    paginator=paginator)
    return build_api_response(response)
