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

        # Estado inicial do app
        self.dark_mode = True
        self.include_subfolders = False
        self.folder = None
        self.all_features = []  # Guardará todos os Features extraídos
        self.file_counter = 0   # Quantidade de arquivos .robot
        self.feature_counter = 0  # Quantidade de blocos Feature
        self.folder_counter = 0   # Quantidade de pastas analisadas

        # ---------- Layout principal ----------
        layout = QVBoxLayout()

        # Checkbox para incluir subpastas
        self.subfolders_checkbox = QCheckBox("Incluir subpastas")
        self.subfolders_checkbox.stateChanged.connect(self.toggle_subfolders)
        layout.addWidget(self.subfolders_checkbox)

        # Botão para selecionar pasta
        self.folder_button = QPushButton("Selecionar Pasta")
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        # Splitter divide tela: lista de arquivos e preview
        splitter = QSplitter(Qt.Horizontal)

        # Lista de arquivos .robot encontrados
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_preview)
        splitter.addWidget(self.file_list)

        # Caixa de preview para mostrar os Features encontrados
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        splitter.addWidget(self.preview)

        splitter.setSizes([250, 650])  # Define tamanhos iniciais
        layout.addWidget(splitter)

        # Botão para gerar .feature consolidado
        self.generate_button = QPushButton("Gerar .feature")
        self.generate_button.clicked.connect(self.generate_feature)
        layout.addWidget(self.generate_button)

        # Botão para trocar o tema
        self.theme_button = QPushButton("Trocar Tema (Claro/Escuro)")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)

        # Caixa de log para debug
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Logs do sistema aparecerão aqui...")
        layout.addWidget(QLabel("Log do sistema:"))
        layout.addWidget(self.log_output)

        # ---------- Widget central ----------
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Aplica tema inicial
        self.apply_theme()

    # -------- Funções de interface --------

    def toggle_subfolders(self, state):
        """Ativa/desativa a inclusão de subpastas"""
        self.include_subfolders = (state == Qt.Checked)
        self.log_output.append(f"[INFO] Incluir subpastas: {self.include_subfolders}")

    def select_folder(self):
        """Seleciona pasta e busca arquivos .robot"""
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta com arquivos .robot")
        if folder:
            # Reset contadores e dados anteriores
            self.file_list.clear()
            self.folder = folder
            self.all_features.clear()
            self.file_counter = 0
            self.feature_counter = 0
            self.folder_counter = 0

            self.log_output.append(f"\n[INFO] Pasta selecionada: {folder}")

            if self.include_subfolders:
                # Busca recursiva
                for root, dirs, files in os.walk(folder):
                    self._process_folder(root, files)
            else:
                # Apenas a pasta raiz
                files = os.listdir(folder)
                self._process_folder(folder, files)

            # Resumo final
            self.log_output.append("\n[RESUMO FINAL]")
            self.log_output.append(f"- Total de pastas analisadas: {self.folder_counter}")
            self.log_output.append(f"- Total de arquivos .robot: {self.file_counter}")
            self.log_output.append(f"- Total de Features extraídas: {self.feature_counter}")

            # Atualiza preview geral
            if self.all_features:
                preview_text = "\n\n---\n\n".join(self.all_features)
            else:
                preview_text = "Nenhum bloco de Feature encontrado nos arquivos."
            self.preview.setPlainText(preview_text)

    def _process_folder(self, folder, files):
        """Processa todos os arquivos .robot de uma pasta"""
        robot_files = [f for f in files if f.lower().endswith(".robot")]
        if not robot_files:
            return

        self.folder_counter += 1
        self.log_output.append(f"\n[INFO] Pasta analisada: {folder}")
        self.log_output.append(f"       - Arquivos .robot encontrados: {len(robot_files)}")

        folder_features_count = 0

        for file in robot_files:
            full_path = os.path.join(folder, file)
            self.file_list.addItem(full_path)
            self.file_counter += 1

            try:
                features = parse_robot_file(full_path)
                if features:
                    self.all_features.extend(features)
                    folder_features_count += len(features)
                    self.feature_counter += len(features)
                    self.log_output.append(f"          > {file}: {len(features)} Feature(s)")
                else:
                    self.log_output.append(f"          > {file}: Nenhum Feature encontrado")
            except Exception as e:
                self.log_output.append(f"[ERRO] Falha ao parsear {full_path}: {e}")

        self.log_output.append(f"       - Total de Features nesta pasta: {folder_features_count}")

    def show_preview(self, item):
        """Mostra Features de um arquivo específico no preview"""
        file_path = item.text()
        try:
            features = parse_robot_file(file_path)
            if features:
                preview_text = "\n\n---\n\n".join(features)
            else:
                preview_text = "Nenhum bloco de Feature encontrado neste arquivo."
        except Exception as e:
            preview_text = f"[ERRO] Falha ao parsear {file_path}: {e}"

        self.preview.setPlainText(preview_text)

    def generate_feature(self):
        """Gera um único arquivo .feature consolidado"""
        if not self.all_features:
            QMessageBox.warning(self, "Aviso", "Nenhum conteúdo para gerar .feature!")
            return

        output_path = os.path.join(self.folder, "combined.feature")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(self.all_features))

            QMessageBox.information(self, "Sucesso", f"Arquivo salvo em:\n{output_path}")
            self.log_output.append(f"[OK] Arquivo .feature gerado em {output_path}")

            # Abre pasta no explorador
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
        """Alterna tema claro/escuro"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Aplica estilos de tema"""
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; color: #ffffff; }
                QPushButton { background-color: #333333; color: #ffffff; border-radius: 5px; padding: 5px; }
                QPushButton:hover { background-color: #444444; }
                QCheckBox { color: #ffffff; }
                QListWidget, QTextEdit { background-color: #1e1e1e; color: #ffffff; }
            """)
        else:
            self.setStyleSheet("")  # tema padrão claro


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
