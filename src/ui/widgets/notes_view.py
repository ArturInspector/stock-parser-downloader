import json
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTextEdit, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt

class NotesViewWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.notes_file = Path("editing_notes.json")
        self.init_ui()
        self.load_notes()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        header = QLabel("Editing Notes")
        header.setObjectName("Header")
        desc = QLabel("Save timestamps, script ideas, and project metadata here.")
        desc.setStyleSheet("color: #71717a; font-size: 14px;")
        
        layout.addWidget(header)
        layout.addWidget(desc)

        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Start typing your notes for CapCut or Premiere Pro...")
        self.editor.setStyleSheet("""
            background-color: #09090b;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 20px;
            font-size: 16px;
            line-height: 1.5;
        """)
        
        layout.addWidget(self.editor)

        # Controls
        controls = QHBoxLayout()
        
        save_btn = QPushButton("Save Notes")
        save_btn.setMinimumHeight(48)
        save_btn.clicked.connect(self.save_notes)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setObjectName("SecondaryButton")
        clear_btn.setMinimumHeight(48)
        clear_btn.clicked.connect(self.clear_notes)
        
        controls.addStretch()
        controls.addWidget(clear_btn)
        controls.addWidget(save_btn)
        
        layout.addLayout(controls)

    def load_notes(self):
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.editor.setPlainText(data.get('content', ''))
            except:
                pass

    def save_notes(self):
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump({'content': self.editor.toPlainText()}, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Success", "Notes saved successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save notes: {e}")

    def clear_notes(self):
        if QMessageBox.question(self, "Confirm", "Are you sure you want to clear all notes?") == QMessageBox.StandardButton.Yes:
            self.editor.clear()
            self.save_notes()
