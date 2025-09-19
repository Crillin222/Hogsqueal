import sys
import os
import platform
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QTextEdit, QMessageBox, QSplitter, QCheckBox
)
from PySide6.QtCore import Qt
from core.parser import parse_robot_file


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot → Cucumber → Jira")
        self.resize(800, 600)

        self.dark_mode = True
        self.include_subfolders = False
        self.folder = None
        self.all_features = []

        layout = QVBoxLayout()

        # Checkbox para incluir subpastas
        self.subfolders_checkbox = QCheckBox("Incluir subpastas")
        self.subfolders_checkbox.stateChanged.connect(self.toggle_subfolders)
        layout.addWidget(self.subfolders_checkbox)

        # Botão para selecionar pasta
        self.folder_button = QPushButton("Selecionar Pasta")
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        splitter = QSplitter(Qt.Horizontal)

        self.file_list = QListWidget()
        splitter.addWidget(self.file_list)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        splitter.addWidget(self.preview)

        splitter.setSizes([200, 600])
        layout.addWidget(splitter)

        self.generate_button = QPushButton("Gerar Único .feature")
        self.generate_button.clicked.connect(self.generate_feature)
        layout.addWidget(self.generate_button)

        self.theme_button = QPushButton("Trocar Tema (Claro/Escuro)")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.apply_theme()

    def toggle_subfolders(self, state):
        self.include_subfolders = state == Qt.Checked

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta com arquivos .robot")
        if folder:
            self.file_list.clear()
            self.folder = folder
            self.all_features.clear()

            if self.include_subfolders:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if file.endswith(".robot"):
                            full_path = os.path.join(root, file)
                            self.file_list.addItem(full_path)
                            self.all_features.extend(parse_robot_file(full_path))
            else:
                for file in os.listdir(folder):
                    if file.endswith(".robot"):
                        full_path = os.path.join(folder, file)
                        self.file_list.addItem(full_path)
                        self.all_features.extend(parse_robot_file(full_path))

            if self.all_features:
                preview_text = "\n\n---\n\n".join(self.all_features)
            else:
                preview_text = "Nenhum bloco de Feature encontrado nos arquivos."
            self.preview.setPlainText(preview_text)

    def generate_feature(self):
        if not self.folder:
            QMessageBox.warning(self, "Aviso", "Nenhuma pasta selecionada!")
            return

        if not self.all_features:
            QMessageBox.warning(self, "Aviso", "Nenhum cucumber encontrado!")
            return

        feature_content = "\n\n".join(self.all_features)
        output_path = os.path.join(self.folder, "consolidado.feature")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(feature_content)

            QMessageBox.information(
                self, "Sucesso",
                f"Arquivo consolidado gerado:\n{output_path}"
            )

            # Abre a pasta no explorador
            self.open_folder(self.folder)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o arquivo:\n{e}")

    def open_folder(self, path):
        """Abre a pasta no explorador do sistema"""
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            os.system(f"open '{path}'")
        else:  # Linux
            os.system(f"xdg-open '{path}'")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; color: #ffffff; }
                QPushButton { background-color: #333333; color: #ffffff; border-radius: 5px; padding: 5px; }
                QPushButton:hover { background-color: #444444; }
                QListWidget, QTextEdit { background-color: #1e1e1e; color: #ffffff; }
                QCheckBox { color: #ffffff; }
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
