from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class ApiSettingsWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header
        header = QLabel("API Configuration")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        desc = QLabel("Manage your API keys for external services.")
        desc.setStyleSheet("color: #a1a1aa; font-size: 14px;")
        layout.addWidget(desc)

        # Settings Container
        container = QFrame()
        container.setObjectName("ContentFrame")
        
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(32)
        container_layout.setContentsMargins(32, 32, 32, 32)

        # Pexels
        self.pexels_input = self.create_api_field(
            container_layout, "Pexels API Key", 
            self.config.pexels_api_key, 
            "https://www.pexels.com/api/"
        )

        # Pixabay
        self.pixabay_input = self.create_api_field(
            container_layout, "Pixabay API Key", 
            self.config.pixabay_api_key,
            "https://pixabay.com/api/docs/"
        )

        # Gemini
        self.gemini_input = self.create_api_field(
            container_layout, "Gemini API Key", 
            self.config.gemini_api_key,
            "https://makersuite.google.com/app/apikey"
        )

        layout.addWidget(container)
        layout.addStretch()

        # Save Button
        save_btn = QPushButton("Save Changes")
        save_btn.setMinimumHeight(48)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def create_api_field(self, parent_layout, label_text, current_value, url):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: 500; color: #e4e4e7;")
        
        link = QLabel(f'<a href="{url}" style="color: #6366f1; text-decoration: none; font-size: 13px;">Get API Key</a>')
        link.setOpenExternalLinks(True)
        link.setCursor(Qt.CursorShape.PointingHandCursor)
        link.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        header_layout.addWidget(label)
        header_layout.addStretch()
        header_layout.addWidget(link)
        
        input_field = QLineEdit()
        input_field.setText(current_value)
        input_field.setPlaceholderText(f"Paste key here...")
        input_field.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addLayout(header_layout)
        layout.addWidget(input_field)
        
        parent_layout.addWidget(wrapper)
        return input_field

    def save_settings(self):
        try:
            self.config.save_api_key('pexels', self.pexels_input.text())
            self.config.save_api_key('pixabay', self.pixabay_input.text())
            self.config.save_api_key('gemini', self.gemini_input.text())
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
