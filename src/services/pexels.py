import requests
from typing import List, Dict, Any
from .api_client import VideoService
from ..utils.logger import logger

class PexelsService(VideoService):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos"

    def search_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.debug("Pexels: Missing API key")
            return []

        headers = {'Authorization': self.api_key}
        url = f'{self.base_url}/search?query={query}&per_page={count}'
        logger.debug(f"Pexels search: {url}")
        
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            raise Exception("Pexels API rate limit exceeded")
        response.raise_for_status()
        
        data = response.json()
        return data.get('videos', [])

    def search_photos(self, query: str, count: int) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []

        headers = {'Authorization': self.api_key}
        url = f'https://api.pexels.com/v1/search?query={query}&per_page={count}'
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        photos = data.get('photos', [])
        # Format to match our internal structure
        results = []
        for p in photos:
            results.append({
                'id': p['id'],
                'url': p['src']['original'],
                'preview': p['src']['large'],
                'width': p['width'],
                'height': p['height'],
                'source': 'Pexels'
            })
        return results

    def get_video_url(self, video_data: Dict[str, Any]) -> str:
        video_files = video_data.get('video_files', [])
        if not video_files:
            return None
        
        # Sort by quality (height)
        video_files.sort(key=lambda x: x.get('height', 0), reverse=True)
        return video_files[0]['link']
