from typing import List

from fastapi import APIRouter
from src.app.service import get_service
from src.config.config import get_config

router = APIRouter(prefix='/storage', tags=['Storage'])
config = get_config()
default_prefix = config.endpoint_path_prefix


@router.get('/unprocessed', response_model=List[str])
async def get_storage_unprocessed(limit: int = 20,
                                  prefix: str = default_prefix):
    """Get a list of unprocessed objects in S3 storage"""
    return get_service().get_storage_unprocessed(limit, prefix)


@router.get('/folders', response_model=List[str])
async def get_storage_folders(prefix: str = default_prefix):
    """Get a list of folders in s3 storage"""
    return get_service().get_storage_folders(prefix)
