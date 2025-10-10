from PySide6.QtWidgets import QApplication
import resources_rc
resources_rc.qInitResources()

def apply_theme(dark_mode: bool):
    """
    Applies the global stylesheet for dark or light mode.
    """
    app = QApplication.instance()
    app.setStyleSheet("")  # Clear previous style

    if dark_mode:
        style = """
            QMainWindow, QWidget { background-color: #121212; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid #4a4a4a;
            }
            QPushButton:hover { background-color: #444444; }
            QListWidget, QTextEdit, QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
            QPushButton#btnSubfolders {
                background: #2c2c2c;
                border: 1px solid #4a4a4a;
                color: #ffffff;
            }
            QPushButton#btnSubfolders:hover { background: #3a3a3a; }
            QPushButton#btnSubfolders:checked {
                background: #2d7d46;
                color: #ffffff;
                border-color: #2d7d46;
            }
            QPushButton#btnSubfolders:checked:hover { background: #2f8b4f; }
            QToolButton#btnTheme {
                border: none;
                padding: 4px;
                margin: 2px;
                border-radius: 6px;
            }
            QToolButton#btnTheme:hover { background: rgba(255,255,255,0.08); }
            QFrame#footerBar {
                background-color: #121212;
                border-top: 1px solid #2a2a2a;
            }
            QLabel#lblSummary { color: #aaaaaa; }
            QSplitter#mainSplitter::handle {
                background-color: #1b1b1b;
                border: none;
                margin: 0;
            }
            QSplitter#mainSplitter::handle:horizontal {
                width: 8px;
                border-left: 1px solid rgba(255,255,255,0.06);
                background-clip: padding;
            }
            QSplitter#mainSplitter::handle:horizontal:hover {
                background-color: #252525;
                border-left-color: rgba(255,255,255,0.14);
            }
            QSplitter#mainSplitter::handle:horizontal:pressed {
                background-color: #2a2a2a;
                border-left-color: rgba(255,255,255,0.18);
            }
        """
    else:
        style = """
            QMainWindow, QWidget { background-color: #f7f7f7; color: #222222; }
            QLabel { color: #222222; }
            QPushButton {
                background-color: #ffffff;
                color: #222222;
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid #bdbdbd;
            }
            QPushButton:hover { background-color: #f0f0f0; }
            QListWidget, QTextEdit, QLineEdit {
                background-color: #ffffff;
                color: #222222;
                border: 1px solid #dcdcdc;
            }
            QPushButton#btnSubfolders {
                background: #f6f6f6;
                border: 1px solid #bdbdbd;
                color: #333333;
            }
            QPushButton#btnSubfolders:hover { background: #eeeeee; }
            QPushButton#btnSubfolders:checked {
                background: #2d7d46;
                color: #ffffff;
                border-color: #2d7d46;
            }
            QPushButton#btnSubfolders:checked:hover { background: #2f8b4f; }
            QToolButton#btnTheme {
                border: none;
                padding: 4px;
                margin: 2px;
                border-radius: 6px;
            }
            QToolButton#btnTheme:hover { background: rgba(0,0,0,0.08); }
            QFrame#footerBar {
                background-color: #f7f7f7;
                border-top: 1px solid #dcdcdc;
            }
            QLabel#lblSummary { color: #555555; }
            QSplitter#mainSplitter::handle {
                background-color: rgba(0,0,0,0.04);
                border: none;
                margin: 0;
            }
            QSplitter#mainSplitter::handle:horizontal {
                width: 8px;
                border-left: 1px solid #dcdcdc;
                background-clip: padding;
            }
            QSplitter#mainSplitter::handle:horizontal:hover {
                background-color: rgba(0,0,0,0.08);
                border-left-color: #c8c8c8;
            }
            QSplitter#mainSplitter::handle:horizontal:pressed {
                background-color: rgba(0,0,0,0.10);
                border-left-color: #bdbdbd;
            }
        """
    app.setStyleSheet(style)