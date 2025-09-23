import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QToolButton, QVBoxLayout, QWidget
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon

import resources_rc
from pages.feature_creator import FeatureCreatorPage
from pages.xray_test import XrayTestPage
from core.theme import apply_theme

resources_rc.qInitResources()

class MainWindow(QMainWindow):
    """
    Main application window. Handles tab navigation and theme switching.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hobgoblin")
        self.resize(900, 600)
        self.dark_mode = True

        # Tabs for navigation
        self.tabs = QTabWidget()
        self.feature_creator_page = FeatureCreatorPage(self)
        self.xray_test_page = XrayTestPage(self)
        self.tabs.addTab(self.feature_creator_page, "Create .feature file")
        self.tabs.addTab(self.xray_test_page, "Create Jira Test")

        # Theme switch button in the top right corner
        self.theme_button = QToolButton(self)
        self.theme_button.setObjectName("btnTheme")
        self.theme_button.setToolTip("Switch theme")
        self.theme_button.setAutoRaise(True)
        self.theme_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.theme_button.setIconSize(QSize(20, 20))
        self.theme_button.setIcon(QIcon(":/icons/sun.svg"))
        self.theme_button.clicked.connect(self.toggle_theme)
        self.tabs.setCornerWidget(self.theme_button, Qt.TopRightCorner)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Apply initial theme
        self.apply_theme()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        apply_theme(self.dark_mode)
        # Update theme icon
        if self.dark_mode:
            self.theme_button.setIcon(QIcon(":/icons/sun.svg"))
        else:
            self.theme_button.setIcon(QIcon(":/icons/moon.svg"))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
