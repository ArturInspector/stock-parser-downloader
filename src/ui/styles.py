
MINIMALIST_THEME = """
/* Global Reset and Base Colors */
QMainWindow {
    background-color: #18181b; /* Zinc 950 */
}

QWidget {
    color: #e4e4e7; /* Zinc 200 */
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
}

/* Frames and Containers */
QFrame {
    background-color: transparent;
    border: none;
}

QFrame#Sidebar {
    background-color: #18181b;
    border-right: 1px solid #27272a; /* Zinc 800 */
}

QFrame#ContentFrame {
    background-color: #27272a; /* Zinc 800 */
    border-radius: 16px;
    border: 1px solid #3f3f46; /* Zinc 700 */
}

QFrame#Card {
    background-color: #27272a;
    border-radius: 12px;
    border: 1px solid #3f3f46;
}

/* Inputs */
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background-color: #18181b;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 12px 16px;
    color: #ffffff;
    font-size: 14px;
    selection-background-color: #6366f1; /* Indigo 500 */
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
    border: 1px solid #818cf8; /* Indigo 400 */
    background-color: #27272a;
}

QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QTextEdit:hover {
    border: 1px solid #52525b; /* Zinc 600 */
}

/* Buttons */
QPushButton {
    background-color: #6366f1; /* Indigo 500 */
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #4f46e5; /* Indigo 600 */
}

QPushButton:pressed {
    background-color: #4338ca; /* Indigo 700 */
}

QPushButton:disabled {
    background-color: #3f3f46;
    color: #71717a;
}

QPushButton#SecondaryButton {
    background-color: transparent;
    border: 1px solid #3f3f46;
    color: #e4e4e7;
}

QPushButton#SecondaryButton:hover {
    background-color: #27272a;
    border: 1px solid #52525b;
    color: #ffffff;
}

QPushButton#NavButton {
    background-color: transparent;
    text-align: left;
    padding: 12px 16px;
    border-radius: 8px;
    border: none;
    color: #a1a1aa; /* Zinc 400 */
    font-weight: 500;
    margin: 4px 0px;
}

QPushButton#NavButton:checked {
    background-color: #27272a;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#NavButton:hover:!checked {
    background-color: #27272a;
    color: #e4e4e7;
}

/* Lists */
QListWidget {
    background-color: #18181b;
    border: 1px solid #3f3f46;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 4px;
    color: #e4e4e7;
}

QListWidget::item:selected {
    background-color: #27272a;
    color: #ffffff;
    border: 1px solid #3f3f46;
}

QListWidget::item:hover:!selected {
    background-color: #27272a;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #3f3f46;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #52525b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Progress Bar */
QProgressBar {
    background-color: #27272a;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: transparent;
    height: 4px;
}

QProgressBar::chunk {
    background-color: #6366f1;
    border-radius: 4px;
}

/* Labels */
QLabel#Header {
    font-size: 24px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 8px;
}

QLabel#SubHeader {
    font-size: 14px;
    font-weight: 600;
    color: #a1a1aa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

QLabel#SmallText {
    font-size: 12px;
    color: #52525b;
}
"""
