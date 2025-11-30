from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QStackedWidget, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor
from .styles import MINIMALIST_THEME
from .widgets.api_settings import ApiSettingsWidget
from .widgets.search_view import SearchViewWidget
from ..config import Config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Stock Video Downloader')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(MINIMALIST_THEME)

        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        main_layout.addWidget(content_container)

        # Initialize pages
        self.search_view = SearchViewWidget(self.config)
        self.api_settings = ApiSettingsWidget(self.config)

        self.content_stack.addWidget(self.search_view)
        self.content_stack.addWidget(self.api_settings)

        # Default page
        self.nav_search.setChecked(True)

    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(24, 48, 24, 24)
        layout.setSpacing(8)

        # App Title
        title = QLabel("Stock Parser")
        title.setObjectName("Header")
        title.setStyleSheet("font-size: 20px; font-weight: 600; letter-spacing: -0.5px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Pro Edition")
        subtitle.setObjectName("SmallText")
        subtitle.setStyleSheet("color: #71717a; font-size: 13px; margin-top: -5px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(48)

        # Navigation Buttons
        label = QLabel("MENU")
        label.setObjectName("SubHeader")
        label.setStyleSheet("font-size: 11px; margin-bottom: 4px;")
        layout.addWidget(label)

        self.nav_search = self.create_nav_button("Search Videos", 0)
        self.nav_settings = self.create_nav_button("Settings", 1)
        
        layout.addWidget(self.nav_search)
        layout.addWidget(self.nav_settings)
        
        layout.addStretch()
        
        # Version info
        version = QLabel("Version 2.1.0")
        version.setObjectName("SmallText")
        layout.addWidget(version)

    def create_nav_button(self, text, index):
        btn = QPushButton(text)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_page(index))
        return btn

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
