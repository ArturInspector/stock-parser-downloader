import requests
from pathlib import Path
from typing import Callable, Optional
from .api_client import VideoService

class Downloader:
    def __init__(self, save_path: Path):
        self.save_path = save_path

    def download_video(self, url: str, filename: str, progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                
                # Skip if > 100MB
                if total_size > 100 * 1024 * 1024:
                    return False
                
                file_path = self.save_path / filename
                self.save_path.mkdir(parents=True, exist_ok=True)
                
                downloaded_size = 0
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if progress_callback and total_size > 0:
                                percent = int((downloaded_size / total_size) * 100)
                                progress_callback(percent)
                return True
        except Exception as e:
            print(f"Download error: {e}")
            return False
        return False
