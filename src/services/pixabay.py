import requests
import random
from typing import List, Dict, Any
from .api_client import VideoService

class PixabayService(VideoService):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api/videos/"

    def search_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise ValueError("Pixabay API key is missing")

        params = {
            'key': self.api_key,
            'q': query,
            'per_page': count * 2,  # Request more for better selection
            'lang': 'en',
            'order': 'latest',
            'min_width': 1280,
            'min_height': 720,
            'safesearch': 'true',
            'page': 1
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('hits'):
            # Try second page
            params['page'] = 2
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
        hits = data.get('hits', [])
        random.shuffle(hits)
        return hits[:count]

    def get_video_url(self, video_data: Dict[str, Any]) -> str:
        # Pixabay structure is different
        videos = video_data.get('videos', {})
        for quality in ['large', 'medium', 'small']:
            if videos.get(quality, {}).get('url'):
                return videos[quality]['url']
        return None
