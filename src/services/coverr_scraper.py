import requests
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
from ..utils.logger import logger

class CoverrScraper:
    def __init__(self):
        self.base_url = "https://coverr.co/s"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

    def search_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}?q={query.lower().replace(' ', '+')}"
        logger.debug(f"Coverr search started: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.debug(f"Coverr response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Coverr request failed: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            data_script = soup.find('script', id='__NEXT_DATA__')
            if not data_script:
                logger.warning("Coverr: __NEXT_DATA__ script not found, trying alternate methods")
                # Fallback: search for any script containing video data patterns
                scripts = soup.find_all('script')
                for s in scripts:
                    if s.string and 'urls' in s.string and 'mp4' in s.string:
                        data_script = s
                        break
            
            if data_script and data_script.string:
                try:
                    # Clean the script content if it's not pure JSON
                    json_str = data_script.string
                    if not json_str.strip().startswith('{'):
                        json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                    
                    data = json.loads(json_str)
                    
                    # Dig through properties to find videos
                    memo = []
                    def find_videos_recursive(obj):
                        if isinstance(obj, list):
                            for item in obj:
                                if isinstance(item, dict) and 'urls' in item and 'mp4' in item.get('urls', {}):
                                    memo.append(item)
                                find_videos_recursive(item)
                        elif isinstance(obj, dict):
                            if 'urls' in obj and 'mp4' in obj.get('urls', {}):
                                memo.append(obj)
                            for k, v in obj.items():
                                find_videos_recursive(v)
                    
                    find_videos_recursive(data)
                    logger.debug(f"Coverr extracted {len(memo)} raw items")

                    for v in memo[:count]:
                        video_id = v.get('id')
                        slug = v.get('slug')
                        if not video_id: continue
                        
                        download_url = v.get('urls', {}).get('mp4')
                        if not download_url:
                            download_url = f"https://coverr-video.s3.amazonaws.com/mp4/{slug}.mp4"
                        
                        videos.append({
                            'id': video_id,
                            'title': v.get('title', f"Coverr {video_id}"),
                            'source': 'Coverr',
                            'download_url': download_url,
                            'preview': v.get('thumbnail')
                        })
                except Exception as e:
                    logger.error(f"Coverr JSON parsing error: {e}")
            
            logger.info(f"Coverr search finished: {len(videos)} results")
            return videos
        except Exception as e:
            logger.error(f"Coverr scraper exception: {e}")
            return []
