import sys
import os
import subprocess
import resources_rc

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QTextEdit, QMessageBox,
    QSplitter, QLabel, QToolButton, QFrame
)
from PySide6.QtCore import Qt, QSize
# from PySide6.QtGui import QIcon  # habilite se for usar SVG via .qrc

from core.parser import parse_robot_file

from PySide6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot → Cucumber → Jira")
        self.resize(900, 600)

        # ---------- Estado inicial ----------
        self.dark_mode = True
        self.include_subfolders = False
        self.folder = None
        self.all_features = []

        # Contadores
        self.folder_count = 0
        self.file_count = 0
        self.feature_count = 0
        self.scenario_count = 0

        # ---------- Layout principal ----------
        layout = QVBoxLayout()

        # --- Header (linha superior) ---
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        # Botão para selecionar pasta (à esquerda)
        self.folder_button = QPushButton("Selecionar Pasta")
        self.folder_button.clicked.connect(self.select_folder)
        header.addWidget(self.folder_button)

        # "Checkbox" de subpastas → botão toggle (destacado quando ligado)
        self.subfolders_checkbox = QPushButton("Incluir subpastas")
        self.subfolders_checkbox.setObjectName("btnSubfolders")
        self.subfolders_checkbox.setCheckable(True)
        self.subfolders_checkbox.setChecked(self.include_subfolders)
        self.subfolders_checkbox.setToolTip("Alternar inclusão de subpastas")
        self.subfolders_checkbox.toggled.connect(
            lambda checked: self.toggle_subfolders(Qt.Checked if checked else Qt.Unchecked)
        )
        header.addWidget(self.subfolders_checkbox)

        # Empurra o tema para a direita
        header.addStretch()

        # Botão de tema no canto superior direito (ícone apenas)
        self.theme_button = QToolButton(self)
        self.theme_button.setObjectName("btnTheme")
        self.theme_button.setToolTip("Alternar tema")
        self.theme_button.setAutoRaise(True)
        self.theme_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.theme_button.setIconSize(QSize(20, 20))
        # Ícone inicial com emoji (trocaremos por SVG se quiser)
        self.theme_button.setIcon(QIcon(":/icons/sun.svg") if self.dark_mode else QIcon(":/icons/moon.svg"))
        self.theme_button.setText("")  # sem texto
        self.theme_button.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_button)

        layout.addLayout(header)

        # --- Conteúdo principal: Splitter (lista de arquivos e preview) ---
        splitter = QSplitter(Qt.Horizontal)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_preview)
        splitter.addWidget(self.file_list)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        splitter.addWidget(self.preview)

        splitter.setSizes([250, 650])
        layout.addWidget(splitter, 3)  # dá mais peso ao splitter

        # Logs
        layout.addWidget(QLabel("Log do sistema:"), 0)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Logs do sistema aparecerão aqui...")
        layout.addWidget(self.log_output, 1)  # expande com a janela

        # --- Rodapé fixo (sumário + Gerar .feature) ---
        self.footer = QFrame()
        self.footer.setObjectName("footerBar")
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(12, 6, 12, 6)
        footer_layout.setSpacing(8)

        self.lblSummary = QLabel()
        self.lblSummary.setObjectName("lblSummary")
        footer_layout.addWidget(self.lblSummary)

        footer_layout.addStretch()

        self.generate_button = QPushButton("Gerar .feature")
        self.generate_button.clicked.connect(self.generate_feature)
        footer_layout.addWidget(self.generate_button)

        layout.addWidget(self.footer, 0)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Tema + sumário inicial
        self.apply_theme()
        self._update_summary()

    # --------- Funções ---------

    def _update_summary(self):
        """Atualiza o texto de sumário no rodapé."""
        self.lblSummary.setText(
            f"Pastas: {self.folder_count} • Arquivos: {self.file_count} • "
            f"Features: {self.feature_count} • Cenários: {self.scenario_count}"
        )

    def toggle_subfolders(self, state: int):
        """Ativa/desativa a inclusão de subpastas"""
        self.include_subfolders = (state == Qt.Checked)  # 2 significa "Checked"
        self.log_output.append(f"[INFO] Incluir subpastas: {self.include_subfolders}")

    def select_folder(self):
        """Seleciona pasta raiz e busca arquivos"""
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta com arquivos .robot")
        if folder:
            self.file_list.clear()
            self.folder = folder
            self.all_features.clear()

            # Reinicia contadores
            self.folder_count = 0
            self.file_count = 0
            self.feature_count = 0
            self.scenario_count = 0
            self._update_summary()

            self.log_output.append(f"[INFO] Pasta selecionada: {folder}")

            if self.include_subfolders:
                for root, dirs, files in os.walk(folder):
                    self.folder_count += 1
                    for file in files:
                        self.file_count += 1
                        if file.lower().endswith(".robot"):
                            full_path = os.path.join(root, file)
                            self._process_file(full_path)
            else:
                # Considera apenas a raiz como 1 pasta analisada
                self.folder_count = 1
                for file in os.listdir(folder):
                    self.file_count += 1
                    if file.lower().endswith(".robot"):
                        full_path = os.path.join(folder, file)
                        self._process_file(full_path)

            # Atualiza preview geral
            if self.all_features:
                preview_text = "\n\n---\n\n".join(self.all_features)
            else:
                preview_text = "Nenhum bloco de Feature encontrado nos arquivos."
            self.preview.setPlainText(preview_text)

            # Mostra resumo final no log
            self.log_output.append("\n[RESUMO FINAL]")
            self.log_output.append(f"- Total de pastas analisadas: {self.folder_count}")
            self.log_output.append(f"- Total de arquivos .robot: {self.file_count}")
            self.log_output.append(f"- Total de Features extraídas: {self.feature_count}")
            self.log_output.append(f"- Total de Cenários extraídos: {self.scenario_count}\n")

            # Atualiza o sumário do rodapé
            self._update_summary()

    def _process_file(self, full_path):
        """Processa um único arquivo .robot"""
        self.file_list.addItem(full_path)
        try:
            features, stats = parse_robot_file(full_path)

            if features:
                self.all_features.extend(features)
                self.feature_count += stats["features"]
                self.scenario_count += stats["scenarios"]

                self.log_output.append(
                    f"[OK] {os.path.basename(full_path)} → "
                    f"{stats['features']} Feature(s), {stats['scenarios']} Cenário(s)"
                )
            else:
                self.log_output.append(f"[WARN] Nenhum Feature encontrado em {full_path}")

        except Exception as e:
            self.log_output.append(f"[ERRO] Falha ao parsear {full_path}: {e}")

    def show_preview(self, item):
        """Preview de um arquivo"""
        file_path = item.text()
        try:
            features, _ = parse_robot_file(file_path)
            if features:
                preview_text = "\n\n---\n\n".join(features)
            else:
                preview_text = "Nenhum bloco de Feature encontrado neste arquivo."
        except Exception as e:
            preview_text = f"[ERRO] Falha ao parsear {file_path}: {e}"
        self.preview.setPlainText(preview_text)

    def generate_feature(self):
        """Gera arquivo .feature consolidado"""
        if not self.all_features:
            QMessageBox.warning(self, "Aviso", "Nenhum conteúdo para gerar .feature!")
            return
        output_path = os.path.join(self.folder, "combined.feature")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(self.all_features))

            QMessageBox.information(self, "Sucesso", f"Arquivo salvo em:\n{output_path}")
            self.log_output.append(f"[OK] Arquivo .feature gerado em {output_path}")

            # Abre no explorador
            if sys.platform == "win32":
                subprocess.Popen(f'explorer /select,"{output_path}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", output_path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(output_path)])

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar arquivo: {e}")
            self.log_output.append(f"[ERRO] Falha ao salvar arquivo: {e}")

    def toggle_theme(self):
        """Troca tema claro/escuro"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()           # aplica paleta/estilo
        self._update_theme_icon()    # atualiza ícone (sol/lua)

    def _update_theme_icon(self):
        if isinstance(self.theme_button, QToolButton):
            self.theme_button.setIcon(QIcon(":/icons/sun.svg") if self.dark_mode else QIcon(":/icons/moon.svg"))
            self.theme_button.setText("")


    def apply_theme(self):
        """Aplica o tema (inclui estilos do header e do rodapé)"""
        if self.dark_mode:
            style = """
                QMainWindow { background-color: #121212; color: #ffffff; }
                QLabel { color: #ffffff; }

                QPushButton {
                    background-color: #333333;
                    color: #ffffff;
                    border-radius: 6px;
                    padding: 6px 10px;
                    border: 1px solid #4a4a4a;
                }
                QPushButton:hover { background-color: #444444; }

                QListWidget, QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #2a2a2a;
                }

                /* Botão toggle 'Incluir subpastas' */
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

                /* Botão do tema (ícone) */
                QToolButton#btnTheme {
                    border: none;
                    padding: 4px;
                    margin: 2px;
                    border-radius: 6px;
                }
                QToolButton#btnTheme:hover { background: rgba(255,255,255,0.08); }

                /* Rodapé */
                QFrame#footerBar {
                    background-color: #121212;
                    border-top: 1px solid #2a2a2a;
                }
                QLabel#lblSummary {
                    color: #aaaaaa;
                }
            """
        else:
            style = """
                QMainWindow { background-color: #f7f7f7; color: #222222; }
                QLabel { color: #222222; }

                QPushButton {
                    background-color: #ffffff;
                    color: #222222;
                    border-radius: 6px;
                    padding: 6px 10px;
                    border: 1px solid #bdbdbd;
                }
                QPushButton:hover { background-color: #f0f0f0; }

                QListWidget, QTextEdit {
                    background-color: #ffffff;
                    color: #222222;
                    border: 1px solid #dcdcdc;
                }

                /* Botão toggle 'Incluir subpastas' */
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

                /* Botão do tema (ícone) */
                QToolButton#btnTheme {
                    border: none;
                    padding: 4px;
                    margin: 2px;
                    border-radius: 6px;
                }
                QToolButton#btnTheme:hover { background: rgba(0,0,0,0.08); }

                /* Rodapé */
                QFrame#footerBar {
                    background-color: #f7f7f7;
                    border-top: 1px solid #dcdcdc;
                }
                QLabel#lblSummary {
                    color: #555555;
                }
            """
        self.setStyleSheet(style)
        self._update_theme_icon()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
