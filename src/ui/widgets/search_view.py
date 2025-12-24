from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QComboBox, QSpinBox, QProgressBar, 
                            QTextEdit, QFileDialog, QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from ...services.pexels import PexelsService
from ...services.pixabay import PixabayService
from ...services.mixkit_scraper import MixkitScraper
from ...services.coverr_scraper import CoverrScraper
from ...services.videezy_scraper import VideezyScraper
from ...services.mazwai_scraper import MazwaiScraper
from ...services.gemini import GeminiService
from ...services.downloader import Downloader
from ...utils.logger import logger
from ...utils.persistence import persistence
from .tilt_card import TiltCard

class SearchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, service_type, query, count, config):
        super().__init__()
        self.service_type = service_type
        self.query = query
        self.count = count
        self.config = config

    def run(self):
        logger.info(f"SearchWorker started: type={self.service_type}, query='{self.query}'")
        try:
            results = []
            
            # Mixkit (Public)
            if self.service_type in ['Mixkit', 'Public Only', 'All Sources']:
                mixkit = MixkitScraper()
                results.extend(mixkit.search_videos(self.query, self.count))
                
            # Coverr (Public)
            if self.service_type in ['Coverr', 'Public Only', 'All Sources']:
                coverr = CoverrScraper()
                results.extend(coverr.search_videos(self.query, self.count))

            # Videezy (Public)
            if self.service_type in ['Videezy', 'Public Only', 'All Sources']:
                videezy = VideezyScraper()
                results.extend(videezy.search_videos(self.query, self.count))

            # Mazwai (Public)
            if self.service_type in ['Mazwai', 'Public Only', 'All Sources']:
                mazwai = MazwaiScraper()
                results.extend(mazwai.search_videos(self.query, self.count))

            # Pexels (Key required)
            if self.service_type in ['Pexels', 'All Sources']:
                if self.config.pexels_api_key:
                    logger.debug("Pexels search enabled with key")
                    pexels = PexelsService(self.config.pexels_api_key)
                    videos = pexels.search_videos(self.query, self.count)
                    for v in videos:
                        v['source'] = 'Pexels'
                        v['download_url'] = pexels.get_video_url(v)
                    results.extend(videos)
                else:
                    logger.debug("Pexels skipped: No API Key")

            # Pixabay (Key required)
            if self.service_type in ['Pixabay', 'All Sources']:
                if self.config.pixabay_api_key:
                    logger.debug("Pixabay search enabled with key")
                    pixabay = PixabayService(self.config.pixabay_api_key)
                    videos = pixabay.search_videos(self.query, self.count)
                    for v in videos:
                        v['source'] = 'Pixabay'
                        v['download_url'] = pixabay.get_video_url(v)
                    results.extend(videos)
                else:
                    logger.debug("Pixabay skipped: No API Key")
            
            # Record in history
            persistence.add_history(self.query, self.service_type, len(results))
            
            logger.info(f"SearchWorker finished: {len(results)} total results found")
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"SearchWorker runtime crash: {e}", exc_info=True)
            self.error.emit(f"Critical search error: {str(e)}")

class DownloadWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(int)
    
    def __init__(self, videos, save_path):
        super().__init__()
        self.videos = videos
        self.save_path = Path(save_path)
        self.downloader = Downloader(self.save_path)

    def run(self):
        count = 0
        total = len(self.videos)
        
        import re
        for i, video in enumerate(self.videos, 1):
            self.progress.emit(f"Downloading {i}/{total}...")
            # Sanitize filename
            safe_id = re.sub(r'[^\w\-_.]', '_', str(video['id']).split('?')[0])
            filename = f"{video['source'].lower()}_{safe_id}.mp4"
            if self.downloader.download_video(video['download_url'], filename):
                persistence.add_download(filename, video['source'], str(self.save_path / filename))
                count += 1
                
        self.finished.emit(count)

class SearchViewWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.found_videos = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        header = QLabel("Search Videos")
        header.setObjectName("Header")
        
        desc = QLabel("Find and download high-quality stock footage.")
        desc.setStyleSheet("color: #71717a; font-size: 14px;")
        
        header_layout.addWidget(header)
        header_layout.addWidget(desc)
        layout.addLayout(header_layout)

        # Search Controls
        controls_frame = QFrame()
        controls_frame.setObjectName("ContentFrame")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(24, 24, 24, 24)
        controls_layout.setSpacing(24)
        
        # Row 1: Query and Service
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("What are you looking for?")
        self.query_input.setMinimumHeight(48)
        
        self.service_combo = QComboBox()
        self.service_combo.addItems(['Public Only', 'All Sources', 'Mixkit', 'Coverr', 'Videezy', 'Mazwai', 'Pexels', 'Pixabay'])
        self.service_combo.setCurrentText('Public Only')
        self.service_combo.setMinimumHeight(48)
        self.service_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        self.count_spin.setSuffix(" videos")
        self.count_spin.setFixedWidth(120)
        self.count_spin.setMinimumHeight(48)
        
        row1.addWidget(self.query_input)
        row1.addWidget(self.service_combo)
        row1.addWidget(self.count_spin)
        
        controls_layout.addLayout(row1)
        
        # Row 2: AI Assistant
        ai_frame = QFrame()
        ai_frame.setObjectName("Card")
        ai_frame.setStyleSheet("background-color: #09090b; border: 1px dashed #27272a;")
        ai_layout = QVBoxLayout(ai_frame)
        ai_layout.setContentsMargins(20, 20, 20, 20)
        
        ai_header = QHBoxLayout()
        ai_label = QLabel("AI Assistant")
        ai_label.setStyleSheet("font-weight: 600; color: #fafafa;")
        ai_header.addWidget(ai_label)
        ai_header.addStretch()
        
        ai_layout.addLayout(ai_header)
        
        self.scenario_input = QTextEdit()
        self.scenario_input.setPlaceholderText("Describe your scene to generate optimized search terms...")
        self.scenario_input.setMaximumHeight(80)
        self.scenario_input.setStyleSheet("background-color: transparent; border: none; padding: 0px;")
        
        gen_btn = QPushButton("Generate Prompts")
        gen_btn.setObjectName("SecondaryButton")
        gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_btn.clicked.connect(self.generate_prompts)
        
        ai_layout.addWidget(self.scenario_input)
        ai_layout.addWidget(gen_btn)
        
        controls_layout.addWidget(ai_frame)
        layout.addWidget(controls_frame)

        # Results Area
        results_label = QLabel("RESULTS")
        results_label.setObjectName("SubHeader")
        layout.addWidget(results_label)

        # Scrollable area for cards
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

        # Bottom Controls
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)
        
        self.path_input = QLineEdit()
        self.path_input.setText(str(self.config.default_download_path))
        self.path_input.setMinimumHeight(48)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("SecondaryButton")
        browse_btn.setMinimumHeight(48)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self.browse_path)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.setMinimumHeight(48)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.start_search)
        
        self.download_btn = QPushButton("Download All")
        self.download_btn.setEnabled(False)
        self.download_btn.setMinimumHeight(48)
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.clicked.connect(self.start_download)
        
        bottom_layout.addWidget(self.path_input)
        bottom_layout.addWidget(browse_btn)
        bottom_layout.addWidget(self.search_btn)
        bottom_layout.addWidget(self.download_btn)
        
        layout.addLayout(bottom_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

    def generate_prompts(self):
        scenario = self.scenario_input.toPlainText()
        if not scenario:
            return
            
        try:
            gemini = GeminiService(self.config.gemini_api_key)
            prompts = gemini.generate_prompts(scenario)
            
            if prompts:
                self.query_input.setText(prompts[0])
                QMessageBox.information(self, "AI Assistant", 
                    "Generated prompts:\n" + "\n".join(f"• {p}" for p in prompts))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"AI Error: {str(e)}")

    def start_search(self):
        query = self.query_input.text()
        if not query:
            return
            
        self.search_btn.setEnabled(False)
        # Clear results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.found_videos = []
        
        self.worker = SearchWorker(
            self.service_combo.currentText(),
            query,
            self.count_spin.value(),
            self.config
        )
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.start()

    def on_search_finished(self, results):
        self.search_btn.setEnabled(True)
        self.found_videos = results
        
        for video in results:
            duration = video.get('duration', '?')
            quality = f"{video.get('width', 0)}x{video.get('height', 0)}"
            title = f"Video {video['id']}"
            subtitle = f"{video['source']} | {quality} | {duration}s"
            
            card = TiltCard(title, subtitle, video.get('preview'))
            self.results_layout.addWidget(card)
            
        if results:
            self.download_btn.setEnabled(True)
            QMessageBox.information(self, "Search", f"Found {len(results)} videos")
        else:
            QMessageBox.information(self, "Search", "No videos found")

    def on_search_error(self, error):
        self.search_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Search failed: {error}")

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if path:
            self.path_input.setText(path)

    def start_download(self):
        if not self.found_videos:
            return
            
        self.download_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        self.dl_worker = DownloadWorker(self.found_videos, self.path_input.text())
        self.dl_worker.progress.connect(self.progress_bar.setFormat)
        self.dl_worker.finished.connect(self.on_download_finished)
        self.dl_worker.start()

    def on_download_finished(self, count):
        self.download_btn.setEnabled(True)
        self.progress_bar.hide()
        QMessageBox.information(self, "Success", f"Downloaded {count} videos successfully")
