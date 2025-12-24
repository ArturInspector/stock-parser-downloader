import requests
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from ..utils.logger import logger

class MixkitScraper:
    def __init__(self):
        self.base_url = "https://mixkit.co/free-stock-video"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

    def search_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        search_term = query.lower().replace(' ', '-')
        url = f"{self.base_url}/{search_term}/"
        logger.debug(f"Mixkit search started: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.debug(f"Mixkit response: {response.status_code}")
            
            if response.status_code != 200:
                url = f"https://mixkit.co/search/videos/{query.lower().replace(' ', '%20')}/"
                logger.debug(f"Retrying Mixkit with search URL: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Mixkit request failed: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            # Mixkit video cards often use generic classes or data attributes
            items = soup.find_all('div', class_=re.compile(r'video-card'))
            if not items:
                # Fallback: look for any links that look like video pages
                items = soup.find_all('a', href=re.compile(r'/free-stock-video/.*-\d+/'))
            
            logger.debug(f"Mixkit found potential items: {len(items)}")

            for item in items[:count]:
                try:
                    # Handle both div-based and a-based items
                    if item.name == 'a':
                        href = item['href']
                        title_tag = item.find(['p', 'h2', 'span'])
                        title = title_tag.text if title_tag else "Mixkit Video"
                    else:
                        link_tag = item.find('a')
                        if not link_tag: continue
                        href = link_tag['href']
                        title_tag = item.find(['p', 'h2', 'span'])
                        title = title_tag.text if title_tag else "Mixkit Video"

                    video_id_match = re.search(r'-(\d+)/?$', href)
                    if not video_id_match: continue
                    
                    video_id = video_id_match.group(1)
                    download_url = f"https://assets.mixkit.co/videos/{video_id}/{video_id}-720.mp4"
                    
                    videos.append({
                        'id': video_id,
                        'title': title.strip(),
                        'source': 'Mixkit',
                        'download_url': download_url,
                        'preview': f"https://assets.mixkit.co/videos/{video_id}/{video_id}-thumb.jpg"
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Mixkit item: {e}")
                    continue
                    
            logger.info(f"Mixkit search finished: {len(videos)} results")
            return videos
        except Exception as e:
            logger.error(f"Mixkit scraper exception: {e}")
            return []
