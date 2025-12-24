from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QPushButton)
from PyQt6.QtCore import Qt
from ...utils.persistence import persistence

class HistoryViewWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        header_layout = QHBoxLayout()
        header = QLabel("Search History")
        header.setObjectName("Header")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(100)
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.clicked.connect(self.refresh_history)
        
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
        
        self.refresh_history()

    def refresh_history(self):
        # Clear existing
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        history = persistence.get_history()
        if not history:
            msg = QLabel("No search history found.")
            msg.setStyleSheet("color: #71717a; padding: 40px;")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.container_layout.addWidget(msg)
            return

        for entry in history:
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
            query = QLabel(entry['query'])
            query.setStyleSheet("font-weight: 600; color: #fafafa; font-size: 15px;")
            
            source = QLabel(f"Source: {entry['source']} | Results: {entry['count']}")
            source.setStyleSheet("color: #71717a; font-size: 13px;")
            
            info.addWidget(query)
            info.addWidget(source)
            
            time = QLabel(self._format_time(entry['timestamp']))
            time.setStyleSheet("color: #3f3f46; font-size: 12px;")
            
            c_layout.addLayout(info)
            c_layout.addStretch()
            c_layout.addWidget(time)
            
            self.container_layout.addWidget(card)

    def _format_time(self, iso_str):
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(iso_str)
            return dt.strftime("%b %d, %H:%M")
        except:
            return iso_str
