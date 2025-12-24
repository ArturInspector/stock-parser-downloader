import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ..utils.logger import logger

class MazwaiScraper:
    def __init__(self):
        self.base_url = "https://mazwai.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

    def search_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        search_term = query.lower().replace(' ', '-')
        url = f"{self.base_url}/stock-video-free/{search_term}"
        logger.debug(f"Mazwai search started: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.debug(f"Mazwai response: {response.status_code}")
            
            if response.status_code != 200:
                # Try search URL instead of categorical URL
                url = f"{self.base_url}/search/{query.replace(' ', '+')}"
                logger.debug(f"Retrying Mazwai with search URL: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)

            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            # Mazwai structure: list items with class 'video-clip'
            items = soup.find_all('div', class_='video-clip')
            logger.debug(f"Mazwai potential items: {len(items)}")

            for item in items[:count]:
                try:
                    link = item.find('a')
                    if not link: continue
                    
                    href = link.get('href', '')
                    video_url = urljoin(self.base_url, href)
                    
                    # Thumb
                    img = item.find('img')
                    thumb = img.get('src', '') if img else ""
                    
                    # Mazwai is harder to get direct MP4 without visiting the page
                    # but we can try to find data-attributes if they exist
                    # For now, we provide the link to the video page
                    
                    videos.append({
                        'id': href.split('/')[-2] if '/' in href else "mazwai-video",
                        'title': item.get('data-title', "Mazwai Video"),
                        'source': 'Mazwai',
                        'download_url': video_url,
                        'preview': thumb
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Mazwai item: {e}")
                    continue

            logger.info(f"Mazwai search finished: {len(videos)} results")
            return videos
        except Exception as e:
            logger.error(f"Mazwai scraper exception: {e}")
            return []
