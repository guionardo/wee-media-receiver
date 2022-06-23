from fastapi import APIRouter
from src.app.service import get_service
from src.dto.app_status_response import AppStatusResponse

router = APIRouter(tags=['Statistics'])


@router.get("/", response_model=AppStatusResponse)
async def stats():
    return get_service().get_app_index()
