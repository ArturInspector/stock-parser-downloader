import requests
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QComboBox, QSpinBox, QProgressBar, 
                            QTextEdit, QFileDialog, QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from ...services.pexels import PexelsService
from ...services.pixabay import PixabayService
from ...services.unsplash_scraper import UnsplashScraper
from ...services.burst_scraper import BurstScraper
from ...services.stocksnap_scraper import StocksnapScraper
from ...services.downloader import Downloader
from ...utils.logger import logger
from ...utils.persistence import persistence
from .tilt_card import TiltCard

class PhotoSearchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, service_type, query, count, config):
        super().__init__()
        self.service_type = service_type
        self.query = query
        self.count = count
        self.config = config

    def run(self):
        logger.info(f"PhotoSearchWorker: query='{self.query}'")
        try:
            results = []
            
            # Burst (Public)
            if self.service_type in ['Burst', 'Public Only', 'All Sources']:
                burst = BurstScraper()
                results.extend(burst.search_photos(self.query, self.count))

            # Stocksnap (Public)
            if self.service_type in ['Stocksnap', 'Public Only', 'All Sources']:
                stocksnap = StocksnapScraper()
                results.extend(stocksnap.search_photos(self.query, self.count))

            # Unsplash (Public - often blocked)
            if self.service_type in ['Unsplash', 'All Sources']:
                unsplash = UnsplashScraper()
                results.extend(unsplash.search_photos(self.query, self.count))

            # Pexels (Key required)
            if self.service_type in ['Pexels', 'All Sources']:
                if self.config.pexels_api_key:
                    pexels = PexelsService(self.config.pexels_api_key)
                    photos = pexels.search_photos(self.query, self.count)
                    results.extend(photos)
                else:
                    logger.debug("Pexels Photos: No API Key")

            # Pixabay (Key required)
            if self.service_type in ['Pixabay', 'All Sources']:
                if self.config.pixabay_api_key:
                    pixabay = PixabayService(self.config.pixabay_api_key)
                    photos = pixabay.search_photos(self.query, self.count)
                    results.extend(photos)
                else:
                    logger.debug("Pixabay Photos: No API Key")
            
            # Record in history
            persistence.add_history(self.query, self.service_type, len(results))
            
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"PhotoSearchWorker error: {e}", exc_info=True)
            self.error.emit(str(e))

class ImagesViewWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.found_images = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header
        header = QLabel("Stock Photos")
        header.setObjectName("Header")
        desc = QLabel("Find high-quality images for your edits.")
        desc.setStyleSheet("color: #71717a; font-size: 14px;")
        
        layout.addWidget(header)
        layout.addWidget(desc)

        # Search Controls
        controls_frame = QFrame()
        controls_frame.setObjectName("ContentFrame")
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(24, 24, 24, 24)
        controls_layout.setSpacing(16)
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Search for photos...")
        self.query_input.setMinimumHeight(48)
        
        self.service_combo = QComboBox()
        self.service_combo.addItems(['Public Only', 'All Sources', 'Burst', 'Stocksnap', 'Unsplash', 'Pexels', 'Pixabay'])
        self.service_combo.setCurrentText('Public Only')
        self.service_combo.setFixedWidth(160)
        self.service_combo.setMinimumHeight(48)
        
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(10)
        self.count_spin.setSuffix(" photos")
        self.count_spin.setMinimumHeight(48)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.setMinimumHeight(48)
        self.search_btn.clicked.connect(self.start_search)
        
        controls_layout.addWidget(self.query_input)
        controls_layout.addWidget(self.service_combo)
        controls_layout.addWidget(self.count_spin)
        controls_layout.addWidget(self.search_btn)
        
        layout.addWidget(controls_frame)

        # Results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.results_layout = QHBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(20)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.results_container)
        layout.addWidget(self.scroll_area)

        # Download All
        self.download_btn = QPushButton("Download All Found")
        self.download_btn.setEnabled(False)
        self.download_btn.setMinimumHeight(48)
        self.download_btn.clicked.connect(self.start_download)
        
        layout.addWidget(self.download_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

    def start_search(self):
        query = self.query_input.text()
        if not query: return
        
        self.search_btn.setEnabled(False)
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        self.worker = PhotoSearchWorker(
            self.service_combo.currentText(),
            query,
            self.count_spin.value(),
            self.config
        )
        self.worker.finished.connect(self.on_search_finished)
        self.worker.start()

    def on_search_finished(self, results):
        self.search_btn.setEnabled(True)
        self.found_images = results
        for photo in results:
            card = TiltCard(f"Photo {photo['id']}", f"{photo['source']} | {photo['width']}x{photo['height']}", photo.get('preview'))
            self.results_layout.addWidget(card)
        
        if results:
            self.download_btn.setEnabled(True)

    def start_download(self):
        # reuse Downloader logic or implement simple batch download
        save_path = Path(self.config.default_download_path) / "photos"
        save_path.mkdir(parents=True, exist_ok=True)
        
        self.progress_bar.show()
        self.progress_bar.setRange(0, len(self.found_images))
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        import re
        count = 0
        for i, img in enumerate(self.found_images):
            # Sanitize filename
            raw_id = img['id']
            # Remove query params and illegal characters
            safe_id = re.sub(r'[^\w\-_.]', '_', raw_id.split('?')[0])
            filename = f"{img['source'].lower()}_{safe_id}.jpg"
            try:
                logger.debug(f"Downloading photo: {img['url']}")
                r = requests.get(img['url'], headers=headers, timeout=15, allow_redirects=True)
                if r.status_code == 200:
                    with open(save_path / filename, 'wb') as f:
                        f.write(r.content)
                    persistence.add_download(filename, img['source'], str(save_path / filename))
                    count += 1
                else:
                    logger.error(f"Download failed for {img['url']}: Status {r.status_code}")
            except Exception as e:
                logger.error(f"Download error for {img['url']}: {e}")
            self.progress_bar.setValue(i+1)
            
        self.progress_bar.hide()
        QMessageBox.information(self, "Success", f"Downloaded {count} photos to {save_path}")
