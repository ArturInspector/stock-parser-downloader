from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QComboBox, QSpinBox, QProgressBar, 
                            QTextEdit, QListWidget, QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from ...services.pexels import PexelsService
from ...services.pixabay import PixabayService
from ...services.gemini import GeminiService
from ...services.downloader import Downloader

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
        try:
            results = []
            if self.service_type in ['Pexels', 'Both']:
                pexels = PexelsService(self.config.pexels_api_key)
                videos = pexels.search_videos(self.query, self.count)
                for v in videos:
                    v['source'] = 'Pexels'
                    v['download_url'] = pexels.get_video_url(v)
                results.extend(videos)

            if self.service_type in ['Pixabay', 'Both']:
                pixabay = PixabayService(self.config.pixabay_api_key)
                videos = pixabay.search_videos(self.query, self.count)
                for v in videos:
                    v['source'] = 'Pixabay'
                    v['download_url'] = pixabay.get_video_url(v)
                results.extend(videos)
            
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

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
        
        for i, video in enumerate(self.videos, 1):
            self.progress.emit(f"Downloading {i}/{total}...")
            filename = f"{video['source'].lower()}_{video['id']}.mp4"
            if self.downloader.download_video(video['download_url'], filename):
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
        desc.setStyleSheet("color: #a1a1aa; font-size: 14px;")
        
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
        self.service_combo.addItems(['Pexels', 'Pixabay', 'Both'])
        self.service_combo.setFixedWidth(140)
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
        ai_frame.setStyleSheet("background-color: #18181b; border: 1px dashed #3f3f46;")
        ai_layout = QVBoxLayout(ai_frame)
        ai_layout.setContentsMargins(20, 20, 20, 20)
        
        ai_header = QHBoxLayout()
        ai_label = QLabel("AI Assistant")
        ai_label.setStyleSheet("font-weight: 600; color: #e4e4e7;")
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

        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

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
        
        self.download_btn = QPushButton("Download Selected")
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
            
            # Show prompts in a dialog or menu
            # For now, just set the first one
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
        self.results_list.clear()
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
            item = f"[{video['source']}] Video ID: {video['id']} | {quality} | {duration}s"
            self.results_list.addItem(item)
            
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
