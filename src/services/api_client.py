from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VideoService(ABC):
    @abstractmethod
    def search_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_video_url(self, video_data: Dict[str, Any]) -> str:
        pass
