from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QPushButton)
from PyQt6.QtCore import Qt
import os
import subprocess
from ...utils.persistence import persistence

class DownloadsViewWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        header_layout = QHBoxLayout()
        header = QLabel("Completed Downloads")
        header.setObjectName("Header")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(100)
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.clicked.connect(self.refresh_downloads)
        
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(12)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self.refresh_downloads()

    def refresh_downloads(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        downloads = persistence.get_downloads()
        if not downloads:
            msg = QLabel("No downloads found.")
            msg.setStyleSheet("color: #71717a; padding: 40px;")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.container_layout.addWidget(msg)
            return

        for entry in downloads:
            card = QFrame()
            card.setObjectName("ContentFrame")
            card.setStyleSheet("""
                QFrame#ContentFrame {
                    background-color: #18181b;
                    border: 1px solid #27272a;
                    border-radius: 8px;
                }
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(16, 16, 16, 16)
            
            info = QVBoxLayout()
            name = QLabel(entry['filename'])
            name.setStyleSheet("font-weight: 600; color: #fafafa; font-size: 14px;")
            
            source = QLabel(f"Source: {entry['source']}")
            source.setStyleSheet("color: #71717a; font-size: 13px;")
            
            info.addWidget(name)
            info.addWidget(source)
            
            btn_layout = QHBoxLayout()
            
            open_folder = QPushButton("📁")
            open_folder.setToolTip("Open in folder")
            open_folder.setFixedSize(32, 32)
            open_folder.setObjectName("SecondaryButton")
            open_folder.clicked.connect(lambda checked, p=entry['path']: self._open_path(p))
            
            btn_layout.addWidget(open_folder)
            
            c_layout.addLayout(info)
            c_layout.addStretch()
            c_layout.addLayout(btn_layout)
            
            self.container_layout.addWidget(card)

    def _open_path(self, path):
        if not os.path.exists(path):
            # Try parent directory
            path = os.path.dirname(path)
            
        if os.name == 'nt':
            subprocess.run(['explorer', '/select,', os.path.normpath(path)])
        else:
            subprocess.run(['xdg-open', os.path.dirname(path)])
