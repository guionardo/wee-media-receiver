"""Video processor service"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class VideoProcessorAbstraction(Protocol):
    """Video processor"""

    @abstractmethod
    def process(self, video_id: str):
        """Process video file"""
