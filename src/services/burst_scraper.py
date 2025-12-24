import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ..utils.logger import logger

class BurstScraper:
    def __init__(self):
        self.base_url = "https://burst.shopify.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def search_photos(self, query: str, count: int) -> List[Dict[str, Any]]:
        search_term = query.lower().replace(' ', '+')
        url = f"{self.base_url}/photos/search?q={search_term}"
        logger.debug(f"Burst search started: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.debug(f"Burst response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Burst request failed: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            photos = []
            
            # Burst photo tiles usually have class 'photo-tile' or are inside specific grids
            items = soup.find_all('div', class_='photo-tile')
            logger.debug(f"Burst potential items: {len(items)}")

            for item in items[:count]:
                try:
                    img = item.find('img')
                    if not img: continue
                    
                    link = item.find('a', class_='photo-tile__image-wrapper')
                    if not link: continue
                    
                    preview = img.get('src', '')
                    if not preview.startswith('http'):
                        preview = urljoin(self.base_url, preview)
                        
                    # Burst ID can be extracted from the link href or img src
                    href = link.get('href', '')
                    photo_id = href.split('/')[-1] if href else "burst-photo"
                    
                    # Direct download link logic for Burst:
                    # They usually have a download button on the page. 
                    # For simplicity, we can use the high-res link if findable or the preview.
                    # Usually: https://burst.shopify.com/photos/[id]/download
                    download_url = f"{self.base_url}{href}/download"
                    
                    photos.append({
                        'id': photo_id,
                        'title': img.get('alt', f"Burst {photo_id}"),
                        'source': 'Burst',
                        'url': download_url,
                        'preview': preview,
                        'width': 0,
                        'height': 0
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Burst item: {e}")
                    continue

            logger.info(f"Burst search finished: {len(photos)} results")
            return photos
        except Exception as e:
            logger.error(f"Burst scraper exception: {e}")
            return []
