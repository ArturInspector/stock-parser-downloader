from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTextEdit, QPushButton, QFrame, QMessageBox, QListWidget)
from PyQt6.QtCore import Qt
from ...services.gemini import GeminiService

class ScriptAssetsViewWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        header = QLabel("Script Assistant")
        header.setObjectName("Header")
        desc = QLabel("Paste your video script, and AI will find the best match assets.")
        desc.setStyleSheet("color: #71717a; font-size: 14px;")
        
        layout.addWidget(header)
        layout.addWidget(desc)

        # Main Split
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # Left: Script Input
        left_panel = QVBoxLayout()
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Paste your script here (e.g., 'A man walking in the park, camera follows him...')")
        self.script_input.setStyleSheet("background-color: #09090b; border: 1px solid #27272a; border-radius: 12px; padding: 15px;")
        
        self.analyze_btn = QPushButton("Analyze Script")
        self.analyze_btn.setMinimumHeight(48)
        self.analyze_btn.clicked.connect(self.analyze_script)
        
        left_panel.addWidget(self.script_input)
        left_panel.addWidget(self.analyze_btn)
        
        # Right: Suggested Keywords/Queries
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("SUGGESTED ASSETS"))
        
        self.queries_list = QListWidget()
        self.queries_list.setStyleSheet("background-color: #18181b; border: 1px solid #27272a; border-radius: 12px; padding: 10px;")
        
        self.search_selected_btn = QPushButton("Search Selected")
        self.search_selected_btn.setObjectName("SecondaryButton")
        self.search_selected_btn.setMinimumHeight(48)
        self.search_selected_btn.clicked.connect(self.search_selected)
        
        right_panel.addWidget(self.queries_list)
        right_panel.addWidget(self.search_selected_btn)

        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
        
        layout.addLayout(main_layout)

    def analyze_script(self):
        script = self.script_input.toPlainText()
        if not script: return
        
        try:
            gemini = GeminiService(self.config.gemini_api_key)
            # Use the existing generate_prompts or custom logic
            prompts = gemini.generate_prompts(f"Identify key visual assets needed for this video script and provide search terms: {script}")
            
            self.queries_list.clear()
            if prompts:
                self.queries_list.addItems(prompts)
            else:
                self.queries_list.addItem("No specific keywords found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"AI Analysis failed: {e}")

    def search_selected(self):
        current_item = self.queries_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Info", "Please select a keyword to search")
            return
            
        keyword = current_item.text()
        # Find the search_view in main_window and set query
        # This is a bit hacky, better would be a signal
        parent = self.window()
        if hasattr(parent, 'search_view'):
            parent.search_view.query_input.setText(keyword)
            parent.switch_page(0) # Go to Search Videos
            parent.nav_search.setChecked(True)
            QMessageBox.information(self, "Success", f"Query '{keyword}' sent to Video Search")
