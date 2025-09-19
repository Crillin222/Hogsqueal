import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QTextEdit, QMessageBox, QSplitter, QCheckBox, QLabel
)
from PySide6.QtCore import Qt
from core.parser import parse_robot_file


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

        # Contadores globais
        self.files_count = 0
        self.folders_count = 0
        self.scenarios_count = 0

        # ---------- Layout principal ----------
        layout = QVBoxLayout()

        # Checkbox de subpastas
        self.subfolders_checkbox = QCheckBox("Incluir subpastas")
        self.subfolders_checkbox.stateChanged.connect(self.toggle_subfolders)
        layout.addWidget(self.subfolders_checkbox)

        # Botão para selecionar pasta
        self.folder_button = QPushButton("Selecionar Pasta")
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        # Splitter: lista de arquivos e preview
        splitter = QSplitter(Qt.Horizontal)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_preview)
        splitter.addWidget(self.file_list)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        splitter.addWidget(self.preview)

        splitter.setSizes([250, 650])
        layout.addWidget(splitter)

        # Botão de gerar feature
        self.generate_button = QPushButton("Gerar .feature")
        self.generate_button.clicked.connect(self.generate_feature)
        layout.addWidget(self.generate_button)

        # Botão de tema
        self.theme_button = QPushButton("Trocar Tema (Claro/Escuro)")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)

        # Caixa de log
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Logs do sistema aparecerão aqui...")
        layout.addWidget(QLabel("Log do sistema:"))
        layout.addWidget(self.log_output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.apply_theme()

    # --------- Funções ---------

    def toggle_subfolders(self, state: int):
        """Ativa/desativa a inclusão de subpastas"""
        self.include_subfolders = (state == 2)  # 2 significa "Checked"
        self.log_output.append(f"[INFO] Incluir subpastas: {self.include_subfolders}")


    def select_folder(self):
        """Seleciona pasta raiz e busca arquivos"""
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta com arquivos .robot")
        if folder:
            self.file_list.clear()
            self.folder = folder
            self.all_features.clear()

            # Reinicia contadores
            self.files_count = 0
            self.folders_count = 0
            self.scenarios_count = 0

            self.log_output.append(f"[INFO] Pasta selecionada: {folder}")

            if self.include_subfolders:
                for root, dirs, files in os.walk(folder):
                    self.folders_count += 1
                    for file in files:
                        if file.lower().endswith(".robot"):
                            full_path = os.path.join(root, file)
                            self._process_file(full_path)
            else:
                self.folders_count = 1
                for file in os.listdir(folder):
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
            self.log_output.append(
                f"[RESUMO] Pastas: {self.folders_count}, Arquivos: {self.files_count}, Cenários: {self.scenarios_count}"
            )

    def _process_file(self, full_path):
        """Processa um arquivo individual"""
        self.file_list.addItem(full_path)
        try:
            features, scenarios = parse_robot_file(full_path)
            self.files_count += 1
            self.scenarios_count += scenarios

            if features:
                self.all_features.extend(features)
                self.log_output.append(f"[OK] {len(features)} Features ({scenarios} Scenarios) de {full_path}")
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
        self.apply_theme()

    def apply_theme(self):
        """Aplica o tema"""
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; color: #ffffff; }
                QPushButton { background-color: #333333; color: #ffffff; border-radius: 5px; padding: 5px; }
                QPushButton:hover { background-color: #444444; }
                QCheckBox { color: #ffffff; }
                QListWidget, QTextEdit { background-color: #1e1e1e; color: #ffffff; }
            """)
        else:
            self.setStyleSheet("")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
