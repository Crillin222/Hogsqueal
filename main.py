import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QLabel
)
from PySide6.QtCore import Qt


# Classe principal da janela do aplicativo
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Configuração básica da janela ---
        self.setWindowTitle("Robot → Cucumber → Jira")  # título da janela
        self.setGeometry(200, 200, 600, 400)  # posição inicial (x, y, largura, altura)

        # --- Criação do widget central (onde ficam os elementos da interface) ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)  # coloca como área principal da janela

        # --- Layout vertical (os elementos ficam empilhados de cima para baixo) ---
        layout = QVBoxLayout(central_widget)

        # --- Texto inicial (instrução para o usuário) ---
        self.label = QLabel("Selecione a pasta com arquivos .robot")
        self.label.setAlignment(Qt.AlignCenter)  # centraliza o texto na horizontal
        layout.addWidget(self.label)  # adiciona ao layout

        # --- Botão para selecionar pasta ---
        self.btn_select_folder = QPushButton("Selecionar Pasta")
        # Quando o botão é clicado, chama a função select_folder()
        self.btn_select_folder.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select_folder)

        # --- Lista que vai mostrar os arquivos encontrados ---
        self.list_files = QListWidget()
        layout.addWidget(self.list_files)

        # --- Botão extra (por enquanto é só um placeholder) ---
        self.btn_process = QPushButton("Gerar .feature (placeholder)")
        # Por enquanto ele não faz nada, mas será usado depois
        layout.addWidget(self.btn_process)

    # --- Função chamada quando o usuário clica no botão "Selecionar Pasta" ---
    def select_folder(self):
        """
        Abre uma janela para o usuário escolher uma pasta.
        Depois, percorre os arquivos dessa pasta e adiciona todos os que terminam
        em .robot na lista (list_files).
        """
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta")

        # Se o usuário realmente escolheu uma pasta (não cancelou)
        if folder:
            self.list_files.clear()  # limpa a lista antes de preencher
            for file in os.listdir(folder):  # percorre todos os arquivos da pasta
                if file.endswith(".robot"):  # verifica se o arquivo termina com .robot
                    self.list_files.addItem(file)  # adiciona o nome do arquivo na lista

            # Atualiza o texto do label para mostrar a pasta selecionada
            self.label.setText(f"Pasta selecionada: {folder}")


# --- Ponto de entrada do programa ---
if __name__ == "__main__":
    # QApplication é o "motor" que roda a aplicação Qt
    app = QApplication(sys.argv)

    # Cria a janela principal
    window = MainWindow()
    window.show()  # mostra a janela na tela

    # Executa o loop da aplicação (fica rodando até o usuário fechar)
    sys.exit(app.exec())
