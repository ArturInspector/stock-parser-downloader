import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
import re
from ..utils.logger import logger

class UnsplashScraper:
    def __init__(self):
        self.base_url = "https://unsplash.com/s/photos"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

    def search_photos(self, query: str, count: int) -> List[Dict[str, Any]]:
        search_term = query.lower().replace(' ', '-')
        url = f"{self.base_url}/{search_term}"
        logger.debug(f"Unsplash search started: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.debug(f"Unsplash response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Unsplash request failed: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            photos = []
            
            # Unsplash often stores initial state in a script tag
            # or we can just parse the img tags with specific classes
            # The direct download URL pattern: https://unsplash.com/photos/[id]/download?force=true
            
            # Find image elements
            img_tags = soup.find_all('img', attrs={'srcset': True})
            logger.debug(f"Unsplash potential images: {len(img_tags)}")

            for img in img_tags:
                if len(photos) >= count: break
                
                try:
                    src = img.get('src', '')
                    if 'images.unsplash.com' not in src: continue
                    
                    # Extract ID from URL
                    # Example: https://images.unsplash.com/photo-1501785888041-af3ef285b470?...
                    photo_id_match = re.search(r'photo-([a-zA-Z0-9-]+)', src)
                    if not photo_id_match: continue
                    photo_id = photo_id_match.group(1)
                    
                    # High quality download URL
                    download_url = f"https://unsplash.com/photos/{photo_id}/download?force=true"
                    
                    photos.append({
                        'id': photo_id,
                        'title': img.get('alt', f"Unsplash {photo_id}"),
                        'source': 'Unsplash',
                        'url': download_url,
                        'preview': src,
                        'width': 0, # Scraped doesn't always have metadata
                        'height': 0
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Unsplash item: {e}")
                    continue

            logger.info(f"Unsplash search finished: {len(photos)} results")
            return photos
        except Exception as e:
            logger.error(f"Unsplash scraper exception: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
