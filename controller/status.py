import http

from fastapi import APIRouter

router = APIRouter(tags=["health_checks", "status"])


@router.get("/status", status_code=http.HTTPStatus.OK)
async def status_check():
    return "OK"


@router.get("/deepstatus", status_code=http.HTTPStatus.OK)
async def deep_status_check():
    return "OK"