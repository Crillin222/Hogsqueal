# core/theme.py - VERSÃO FINAL (Ícone Embutido/Sem Arquivos Externos)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

# Este "palavrão" abaixo é o desenho do ícone de "V" (Checkmark) branco convertido em texto.
# Isso evita que você precise ter um arquivo .svg ou .png separado.
CHECKMARK_BASE64 = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTIwIDZMOSAxN0w0IDEyIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg=="

def apply_theme(dark_mode: bool):
    """
    Aplica o tema Claro ou Escuro à aplicação inteira.
    Usa ícones embutidos em Base64 para não depender de arquivos externos.
    """
    app = QApplication.instance()
    if not app:
        return

    app.setStyle("Fusion")
    palette = QPalette()

    if dark_mode:
        # --- PALETA DARK ---
        base_color = QColor(35, 35, 35)
        text_color = Qt.white
        input_base = QColor(45, 45, 45)
        highlight = QColor(42, 130, 218)
        
        palette.setColor(QPalette.Window, base_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, input_base)
        palette.setColor(QPalette.AlternateBase, base_color)
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, base_color)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, highlight)
        palette.setColor(QPalette.Highlight, highlight)
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # --- CSS DARK ---
        qss = f"""
        QTableWidget {{
            gridline-color: #505050;
            background-color: #2d2d2d;
            color: white;
            selection-background-color: #2a82da;
            selection-color: white;
        }}
        QHeaderView::section {{
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #505050;
            padding: 4px;
        }}
        
        /* INDICADORES (DARK) */
        QCheckBox::indicator, QListView::indicator, QTableView::indicator {{
            width: 16px; height: 16px;
            border: 1px solid #666666; border-radius: 3px;
            background: #2d2d2d;
        }}
        /* Marcado: Fundo Azul + Ícone de Visto Embutido */
        QCheckBox::indicator:checked, QListView::indicator:checked, QTableView::indicator:checked {{
            background: #2a82da;
            border: 1px solid #2a82da;
            image: url({CHECKMARK_BASE64});
        }}
        /* Marcado + Selecionado: Borda Branca + Fundo Azul + Ícone */
        QListView::indicator:checked:selected, QTableView::indicator:checked:selected {{
            background: #2a82da;
            border: 1px solid #ffffff;
            image: url({CHECKMARK_BASE64});
        }}

        QCheckBox {{ color: white; spacing: 5px; }}
        QPushButton {{
            background-color: #353535; color: white; border: 1px solid #505050;
            padding: 5px; border-radius: 4px;
        }}
        QPushButton:hover {{ background-color: #404040; }}
        QPushButton:checked {{ background-color: #2a82da; color: white; border: 1px solid #2a82da; }}
        QLineEdit, QTextEdit, QListWidget {{
            border: 1px solid #505050; border-radius: 4px;
            background-color: #2d2d2d; color: white;
        }}
        """

    else:
        # --- PALETA LIGHT ---
        base_color = QColor(240, 240, 240)
        text_color = Qt.black
        input_base = Qt.white
        highlight = QColor(0, 120, 215)
        
        palette.setColor(QPalette.Window, base_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, input_base)
        palette.setColor(QPalette.AlternateBase, QColor(233, 231, 227))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, base_color)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, highlight)
        palette.setColor(QPalette.Highlight, highlight)
        palette.setColor(QPalette.HighlightedText, Qt.white)

        # --- CSS LIGHT ---
        qss = f"""
        QTableWidget {{
            gridline-color: #d0d0d0;
            background-color: white;
            color: black;
            selection-background-color: #0078d7;
            selection-color: white;
        }}
        QHeaderView::section {{
            background-color: #f0f0f0;
            color: black;
            border: 1px solid #d0d0d0;
            padding: 4px;
        }}
        
        /* INDICADORES (LIGHT) */
        /* Correção da Borda: Cinza escuro para visibilidade no branco */
        QCheckBox::indicator, QListView::indicator, QTableView::indicator {{
            width: 14px; height: 14px;
            border: 2px solid #555555; 
            border-radius: 3px;
            background: #f5f5f5;
        }}
        
        QCheckBox::indicator:hover, QListView::indicator:hover, QTableView::indicator:hover {{
            border-color: #0078d7; background: #ffffff;
        }}
        
        /* Marcado: Fundo Azul + Ícone de Visto Embutido */
        QCheckBox::indicator:checked, QListView::indicator:checked, QTableView::indicator:checked {{
            background: #0078d7;
            border: 2px solid #0078d7;
            image: url({CHECKMARK_BASE64});
        }}
        
        /* Marcado + Selecionado: Borda Branca + Fundo Azul + Ícone */
        QListView::indicator:checked:selected, QTableView::indicator:checked:selected {{
            background: #0078d7;
            border: 2px solid #ffffff;
            image: url({CHECKMARK_BASE64});
        }}

        QCheckBox {{ color: black; spacing: 5px; }}
        QPushButton {{
            background-color: #e1e1e1; color: black; border: 1px solid #adadad;
            padding: 5px; border-radius: 4px;
        }}
        QPushButton:hover {{ background-color: #e5f1fb; border: 1px solid #0078d7; }}
        QPushButton:checked {{ background-color: #cce8ff; color: black; border: 1px solid #005499; }}
        QLineEdit, QTextEdit, QListWidget {{
            border: 1px solid #888888; border-radius: 4px;
            background-color: white; color: black;
        }}
        """

    app.setPalette(palette)
    app.setStyleSheet(qss)