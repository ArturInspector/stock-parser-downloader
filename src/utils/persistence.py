import json
from pathlib import Path
from datetime import datetime
from .logger import logger

class PersistenceManager:
    def __init__(self):
        self.base_dir = Path.home() / ".stock_parser"
        self.base_dir.mkdir(exist_ok=True)
        
        self.history_file = self.base_dir / "history.json"
        self.downloads_file = self.base_dir / "downloads.json"
        
        self._ensure_files()

    def _ensure_files(self):
        for f in [self.history_file, self.downloads_file]:
            if not f.exists():
                with open(f, 'w', encoding='utf-8') as f_out:
                    json.dump([], f_out)

    def add_history(self, query: str, source: str, result_count: int):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'source': source,
                'count': result_count
            }
            
            data.insert(0, entry)
            # Keep only last 100 entries
            data = data[:100]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Persistence error (history): {e}")

    def add_download(self, filename: str, source: str, path: str):
        try:
            with open(self.downloads_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'filename': filename,
                'source': source,
                'path': path
            }
            
            data.insert(0, entry)
            data = data[:100]
            
            with open(self.downloads_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Persistence error (downloads): {e}")

    def get_history(self):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def get_downloads(self):
        try:
            with open(self.downloads_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

persistence = PersistenceManager()
