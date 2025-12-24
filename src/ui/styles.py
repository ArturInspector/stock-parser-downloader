
MINIMALIST_THEME = """
/* Global Reset and Base Colors */
QMainWindow {
    background-color: #09090b; /* Zinc 950 - Deeper Black */
}

QWidget {
    color: #fafafa; /* Zinc 50 */
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
}

/* Frames and Containers */
QFrame {
    background-color: transparent;
    border: none;
}

QFrame#Sidebar {
    background-color: #09090b;
    border-right: 1px solid #27272a; /* Zinc 800 */
}

QFrame#ContentFrame {
    background-color: #18181b; /* Zinc 900 */
    border-radius: 16px;
    border: 1px solid #27272a;
}

QFrame#Card {
    background-color: #18181b;
    border-radius: 12px;
    border: 1px solid #27272a;
}

/* Inputs */
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 12px 16px;
    color: #ffffff;
    font-size: 14px;
    selection-background-color: #06b6d4; /* Cyan 500 */
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
    border: 1px solid #22d3ee; /* Cyan 400 */
    background-color: #18181b;
}

QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QTextEdit:hover {
    border: 1px solid #3f3f46; /* Zinc 700 */
}

/* Buttons */
QPushButton {
    background-color: #06b6d4; /* Cyan 500 */
    color: #083344; /* Cyan 950 for contrast */
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #22d3ee; /* Cyan 400 */
}

QPushButton:pressed {
    background-color: #0891b2; /* Cyan 600 */
}

QPushButton:disabled {
    background-color: #27272a;
    color: #71717a;
}

QPushButton#SecondaryButton {
    background-color: transparent;
    border: 1px solid #27272a;
    color: #fafafa;
}

QPushButton#SecondaryButton:hover {
    background-color: #18181b;
    border: 1px solid #3f3f46;
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
    background-color: #18181b;
    color: #22d3ee; /* Cyan 400 */
    font-weight: 600;
}

QPushButton#NavButton:hover:!checked {
    background-color: #18181b;
    color: #fafafa;
}

/* Lists */
QListWidget {
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 4px;
    color: #fafafa;
}

QListWidget::item:selected {
    background-color: #18181b;
    color: #22d3ee;
    border: 1px solid #27272a;
}

QListWidget::item:hover:!selected {
    background-color: #18181b;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #27272a;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #3f3f46;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Progress Bar */
QProgressBar {
    background-color: #18181b;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: transparent;
    height: 4px;
}

QProgressBar::chunk {
    background-color: #06b6d4;
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
    color: #71717a;
}

/* Dialogs and Message Boxes */
QMessageBox {
    background-color: #09090b;
}

QMessageBox QLabel {
    color: #a1a1aa; /* Zinc 400 - softer than white */
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 100px;
    padding: 8px 16px;
}
"""

