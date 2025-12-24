import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
from ..utils.logger import logger

class VideezyScraper:
    def __init__(self):
        self.base_url = "https://www.videezy.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

    def search_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        search_term = query.lower().replace(' ', '-')
        url = f"{self.base_url}/free-video/{search_term}"
        logger.debug(f"Videezy search started: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.debug(f"Videezy response: {response.status_code}")
            
            if response.status_code != 200:
                # Try generic search
                url = f"{self.base_url}/search/{query.replace(' ', '+')}"
                logger.debug(f"Retrying Videezy with search URL: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)

            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            items = soup.find_all(['li', 'div'], class_=re.compile(r'video-tile|item'))
            logger.debug(f"Videezy potential items: {len(items)}")

            for item in items[:count]:
                try:
                    link = item.find('a')
                    if not link: continue
                    
                    from urllib.parse import urljoin
                    href = link['href']
                    
                    # Filter out non-video links or sponsored content to sister sites
                    if not any(x in href for x in ['/free-video/', '/search/']) and href.startswith('http'):
                        if 'videezy.com' not in href:
                            continue # Skip non-Videezy sponsored links
                    
                    video_url = urljoin(self.base_url, href)
                    
                    img = item.find('img')
                    thumb = img['src'] if img else ""
                    
                    title_div = item.find(class_=re.compile(r'title|name'))
                    title = title_div.text if title_div else "Videezy Video"
                    
                    videos.append({
                        'id': href.split('/')[-1],
                        'title': title.strip(),
                        'source': 'Videezy',
                        'download_url': video_url,
                        'preview': thumb
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Videezy item: {e}")
                    continue

            logger.info(f"Videezy search finished: {len(videos)} results")
            return videos
        except Exception as e:
            logger.error(f"Videezy scraper exception: {e}")
            return []
