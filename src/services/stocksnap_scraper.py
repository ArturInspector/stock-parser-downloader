import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ..utils.logger import logger

class StocksnapScraper:
    def __init__(self):
        self.base_url = "https://stocksnap.io"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

    def search_photos(self, query: str, count: int) -> List[Dict[str, Any]]:
        search_term = query.lower().replace(' ', '+')
        url = f"{self.base_url}/search/{search_term}"
        logger.debug(f"Stocksnap search started: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.debug(f"Stocksnap response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Stocksnap request failed: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            photos = []
            
            items = soup.find_all('div', class_='photo-grid-item')
            logger.debug(f"Stocksnap potential items: {len(items)}")

            for item in items[:count]:
                try:
                    img = item.find('img')
                    if not img: continue
                    
                    link = item.find('a', class_='photo-link')
                    if not link: continue
                    
                    # Stocksnap images are usually in <img> src
                    preview = img.get('src', '')
                    if not preview.startswith('http'):
                        preview = urljoin(self.base_url, preview)
                        
                    href = link.get('href', '')
                    photo_id = href.split('/')[-1] if href else "stocksnap-photo"
                    
                    # High res download URL pattern for Stocksnap
                    # Usually found on the individual page, but we can try to guess or use preview
                    # For now, use the preview as URL if we can't find direct
                    # Actually, Stocksnap has: https://stocksnap.io/photo/[id]/download
                    download_url = f"{self.base_url}/photo/{photo_id}/download"
                    
                    photos.append({
                        'id': photo_id,
                        'title': img.get('alt', f"Stocksnap {photo_id}"),
                        'source': 'Stocksnap',
                        'url': download_url,
                        'preview': preview,
                        'width': 0,
                        'height': 0
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Stocksnap item: {e}")
                    continue

            logger.info(f"Stocksnap search finished: {len(photos)} results")
            return photos
        except Exception as e:
            logger.error(f"Stocksnap scraper exception: {e}")
            return []
