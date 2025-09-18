import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QLabel, QMessageBox
)
from PySide6.QtCore import Qt


def parse_robot_file(path):
    """
    Lê um arquivo .robot e extrai blocos comentados de Feature/Scenario.
    Retorna uma lista de strings, cada uma representando uma Feature completa.
    """
    features = []
    current_block = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Considerar apenas linhas comentadas com "#"
            if stripped.startswith("#"):
                # Remove o "#" e espaços extras
                uncommented = stripped.lstrip("#").strip()
                if uncommented:  # ignora linhas só com "#"
                    current_block.append(uncommented)
            else:
                # Linha não comentada -> fecha bloco atual se existir
                if current_block:
                    features.append("\n".join(current_block))
                    current_block = []

        # Se acabar o arquivo e ainda tiver um bloco em andamento
        if current_block:
            features.append("\n".join(current_block))

    return features


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot → Cucumber → Jira")
        self.setGeometry(200, 200, 600, 400)

        # --- Widget central e layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Label de instrução ---
        self.label = QLabel("Selecione a pasta com arquivos .robot")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # --- Botão para selecionar pasta ---
        self.btn_select_folder = QPushButton("Selecionar Pasta")
        self.btn_select_folder.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select_folder)

        # --- Lista de arquivos .robot ---
        self.list_files = QListWidget()
        layout.addWidget(self.list_files)

        # --- Botão para gerar .feature ---
        self.btn_process = QPushButton("Gerar .feature do arquivo selecionado")
        self.btn_process.clicked.connect(self.generate_feature)
        layout.addWidget(self.btn_process)

        # --- Variável para guardar a pasta atual ---
        self.current_folder = None

    def select_folder(self):
        """Seleciona a pasta e lista os arquivos .robot nela."""
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta")
        if folder:
            self.current_folder = folder
            self.list_files.clear()
            for file in os.listdir(folder):
                if file.endswith(".robot"):
                    self.list_files.addItem(file)
            self.label.setText(f"Pasta selecionada: {folder}")

    def generate_feature(self):
        """Gera um arquivo .feature a partir do .robot selecionado."""
        selected_items = self.list_files.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo .robot na lista.")
            return

        # Nome do arquivo selecionado
        file_name = selected_items[0].text()
        robot_path = os.path.join(self.current_folder, file_name)

        # Parser do arquivo
        features = parse_robot_file(robot_path)
        if not features:
            QMessageBox.information(self, "Resultado", "Nenhuma Feature encontrada no arquivo.")
            return

        # Junta todas as features em um único texto
        feature_content = "\n\n".join(features)

        # Salva como .feature na mesma pasta
        feature_path = robot_path.replace(".robot", ".feature")
        with open(feature_path, "w", encoding="utf-8") as f:
            f.write(feature_content)

        QMessageBox.information(self, "Sucesso", f"Arquivo .feature gerado:\n{feature_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
