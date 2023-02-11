import http

from fastapi import APIRouter, Depends

from controller.context_manager import build_request_context
from models.base import GenericResponseModel, PaginationRequest
from usecases.ytube_usecase import YTubeUseCase
from utils.utils import build_api_response

video_router = APIRouter(prefix="/v1/video", tags=["video_router", "video"])


@video_router.get("", status_code=http.HTTPStatus.OK)
async def get_videos_metadata(_=Depends(build_request_context), paginator: PaginationRequest = Depends()):
    response: GenericResponseModel = YTubeUseCase.get_videos_metadata(paginator=paginator)
    return build_api_response(response)
