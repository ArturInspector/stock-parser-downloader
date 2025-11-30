import os
from pathlib import Path
from dotenv import load_dotenv, set_key

class Config:
    def __init__(self):
        self.env_path = Path('api.env')
        self.load()

    def load(self):
        load_dotenv(self.env_path)
        self.pexels_api_key = os.getenv('PEXELS_API_KEY', '')
        self.pixabay_api_key = os.getenv('PIXABAY_API_KEY', '')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        
        # Default download path
        self.default_download_path = Path.home() / "Downloads" / "stock_videos"

    def save_api_key(self, service: str, key: str):
        if service.lower() == 'pexels':
            set_key(self.env_path, 'PEXELS_API_KEY', key)
            self.pexels_api_key = key
        elif service.lower() == 'pixabay':
            set_key(self.env_path, 'PIXABAY_API_KEY', key)
            self.pixabay_api_key = key
        elif service.lower() == 'gemini':
            set_key(self.env_path, 'GEMINI_API_KEY', key)
            self.gemini_api_key = key
