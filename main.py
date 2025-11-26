# main.py - VERSÃO CORRETA: ABAS NO TOPO + ZOOM NO CANTO SUPERIOR

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QTabWidget, QToolButton, QLabel
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut

import resources_rc
from pages.feature_creator import FeatureCreatorPage
from pages.xray_test import XrayTestPage
from core.theme import apply_theme

resources_rc.qInitResources()

class MainWindow(QMainWindow):
    """
    Janela principal com navegação por ABAS (Top Navigation) 
    e controles de Zoom/Tema no canto superior direito.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hobgoblin")
        self.resize(1280, 720)
        self.dark_mode = True
        
        # Tamanho base da fonte
        self.current_font_size = 10 

        # --- Navegação por Abas (Restaurada) ---
        self.tabs = QTabWidget()
        self.feature_creator_page = FeatureCreatorPage(self)
        self.xray_test_page = XrayTestPage(self)
        
        self.tabs.addTab(self.feature_creator_page, "Create .feature file")
        self.tabs.addTab(self.xray_test_page, "Create Jira Test")

        # --- Container do Canto Superior Direito ---
        # Para colocar vários botões no canto da aba, criamos um widget container
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(2) # Espaço pequeno entre os botões

        # 1. Botão Zoom Out (-)
        self.btn_zoom_out = QToolButton()
        self.btn_zoom_out.setText("-")
        self.btn_zoom_out.setToolTip("Zoom Out (Ctrl -)")
        self.btn_zoom_out.setFixedSize(24, 24)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        corner_layout.addWidget(self.btn_zoom_out)

        # 2. Botão Zoom Reset / Indicador
        self.btn_zoom_reset = QToolButton()
        self.btn_zoom_reset.setText("100%")
        self.btn_zoom_reset.setToolTip("Reset Zoom (Ctrl 0)")
        self.btn_zoom_reset.setFixedSize(45, 24) # Largura maior para caber 150%
        self.btn_zoom_reset.clicked.connect(self.reset_zoom)
        corner_layout.addWidget(self.btn_zoom_reset)

        # 3. Botão Zoom In (+)
        self.btn_zoom_in = QToolButton()
        self.btn_zoom_in.setText("+")
        self.btn_zoom_in.setToolTip("Zoom In (Ctrl +)")
        self.btn_zoom_in.setFixedSize(24, 24)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        corner_layout.addWidget(self.btn_zoom_in)

        # Espaçador visual pequeno
        spacer = QLabel(" ")
        spacer.setFixedWidth(5)
        corner_layout.addWidget(spacer)

        # 4. Botão de Tema (Restaurado para o topo)
        self.theme_button = QToolButton()
        self.theme_button.setObjectName("btnTheme")
        self.theme_button.setToolTip("Switch theme")
        self.theme_button.setAutoRaise(True)
        self.theme_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.theme_button.setIconSize(QSize(18, 18))
        self.theme_button.clicked.connect(self.toggle_theme)
        corner_layout.addWidget(self.theme_button)

        # Define o container como o widget do canto das abas
        self.tabs.setCornerWidget(corner_widget, Qt.TopRightCorner)

        # --- Layout Principal ---
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # --- Atalhos de Teclado ---
        QShortcut(QKeySequence.ZoomIn, self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("+"), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self).activated.connect(self.zoom_out)
        QShortcut(QKeySequence("-"), self).activated.connect(self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(self.reset_zoom)

        # Aplica configuração inicial
        self.apply_theme()
        self.set_global_font_size(self.current_font_size)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        apply_theme(self.dark_mode)
        if self.dark_mode:
            self.theme_button.setIcon(QIcon(":/icons/sun.svg"))
        else:
            self.theme_button.setIcon(QIcon(":/icons/moon.svg"))

    # --- Lógica de Zoom ---
    def set_global_font_size(self, size):
        """Aplica o tamanho da fonte e FORÇA a atualização da UI."""
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(size)
        app.setFont(font)
        
        # Atualiza o texto da porcentagem (10pt = 100%)
        percentage = int((size / 10.0) * 100)
        self.btn_zoom_reset.setText(f"{percentage}%")
        
        # ### CORREÇÃO DO LAG ###
        # Reaplica o tema atual. Isso força o Qt a redesenhar todos os widgets
        # com a nova fonte imediatamente, sem precisar clicar no botão de tema.
        self.apply_theme()

    def zoom_in(self):
        self.current_font_size += 1
        if self.current_font_size > 24: self.current_font_size = 24
        self.set_global_font_size(self.current_font_size)

    def zoom_out(self):
        self.current_font_size -= 1
        if self.current_font_size < 6: self.current_font_size = 6
        self.set_global_font_size(self.current_font_size)

    def reset_zoom(self):
        self.current_font_size = 10
        self.set_global_font_size(self.current_font_size)

def main():
    # Configurações para High DPI
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/hobgoblin_icon.ico"))
    
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()