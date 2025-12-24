from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QStackedWidget, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor
from .styles import MINIMALIST_THEME
from .widgets.api_settings import ApiSettingsWidget
from .widgets.search_view import SearchViewWidget
from .widgets.downloads_view import DownloadsViewWidget
from .widgets.history_view import HistoryViewWidget
from .widgets.images_view import ImagesViewWidget
from .widgets.notes_view import NotesViewWidget
from .widgets.script_assets_view import ScriptAssetsViewWidget
from ..config import Config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Stock Parser Pro - Editor Edition')
        self.setMinimumSize(1300, 900)
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
        self.images_view = ImagesViewWidget(self.config)
        self.script_view = ScriptAssetsViewWidget(self.config)
        self.downloads_view = DownloadsViewWidget(self.config)
        self.history_view = HistoryViewWidget(self.config)
        self.notes_view = NotesViewWidget(self.config)
        self.api_settings = ApiSettingsWidget(self.config)

        self.content_stack.addWidget(self.search_view)    # 0
        self.content_stack.addWidget(self.images_view)    # 1
        self.content_stack.addWidget(self.script_view)    # 2
        self.content_stack.addWidget(self.downloads_view) # 3
        self.content_stack.addWidget(self.history_view)   # 4
        self.content_stack.addWidget(self.notes_view)     # 5
        self.content_stack.addWidget(self.api_settings)   # 6

        # Default page
        self.nav_search.setChecked(True)

    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(24, 48, 24, 24)
        layout.setSpacing(4)

        # App Title
        title = QLabel("Stock Parser")
        title.setObjectName("Header")
        title.setStyleSheet("font-size: 20px; font-weight: 600; letter-spacing: -0.5px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Editor Pro")
        subtitle.setObjectName("SmallText")
        subtitle.setStyleSheet("color: #71717a; font-size: 13px; margin-top: -5px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(32)

        # Navigation Buttons
        def add_label(text):
            lbl = QLabel(text)
            lbl.setObjectName("SubHeader")
            lbl.setStyleSheet("font-size: 10px; margin-top: 16px; margin-bottom: 4px; color: #3f3f46;")
            layout.addWidget(lbl)

        add_label("SEARCH")
        self.nav_search = self.create_nav_button("Videos Search", 0)
        self.nav_images = self.create_nav_button("Photos Search", 1)
        layout.addWidget(self.nav_search)
        layout.addWidget(self.nav_images)

        add_label("AI TOOLS")
        self.nav_script = self.create_nav_button("Script Assistant", 2)
        layout.addWidget(self.nav_script)

        add_label("EDITING")
        self.nav_notes = self.create_nav_button("Editing Notes", 5)
        self.nav_downloads = self.create_nav_button("Downloads", 3)
        self.nav_history = self.create_nav_button("History", 4)
        layout.addWidget(self.nav_notes)
        layout.addWidget(self.nav_downloads)
        layout.addWidget(self.nav_history)

        add_label("SYSTEM")
        self.nav_settings = self.create_nav_button("Settings", 6)
        layout.addWidget(self.nav_settings)
        
        layout.addStretch()
        
        # Version info
        version = QLabel("Version 3.0.0")
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
        
        # Refresh dynamic views
        if index == 3: # Downloads
            self.downloads_view.refresh_downloads()
        elif index == 4: # History
            self.history_view.refresh_history()
