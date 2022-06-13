from typing import Dict

from pydantic import BaseModel
from src import __description__, __version__


class AppStatusResponse(BaseModel):
    title: str = __description__
    debug: bool = False
    version: str = __version__
    openapi_url: str
    status: Dict[str, int]
