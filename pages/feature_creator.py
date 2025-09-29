import os
import sys
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget,
    QTextEdit, QSplitter, QLabel, QFrame, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
# Importe a função corrigida do seu parser
from core.parser import extract_scenarios_from_robot_file
import resources_rc
resources_rc.qInitResources()

class FeatureCreatorPage(QWidget):
    """
    Page for scanning .robot files, extracting scenarios, and generating a single .feature file.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Variáveis de estado
        self.include_subfolders = False
        self.folder = None
        self.all_scenarios = [] # Alterado de all_features para all_scenarios
        self.project_key = "@PBC14TEST" # Valor inicial
        self.tags = ""
        self.folder_count = 0
        self.file_count = 0
        self.feature_count = 0
        self.scenario_count = 0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        header.addWidget(self.folder_button)

        self.subfolders_checkbox = QPushButton("Include subfolders")
        self.subfolders_checkbox.setObjectName("btnSubfolders")
        self.subfolders_checkbox.setCheckable(True)
        self.subfolders_checkbox.setChecked(self.include_subfolders)
        self.subfolders_checkbox.setToolTip("Toggle subfolder inclusion")
        self.subfolders_checkbox.toggled.connect(
            lambda checked: self.toggle_subfolders(Qt.Checked if checked else Qt.Unchecked)
        )
        header.addWidget(self.subfolders_checkbox)

        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("Project (@KEYDOTESTE)")
        self.project_input.setText(self.project_key)
        self.project_input.textChanged.connect(self._on_project_changed)
        header.addWidget(self.project_input)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (@tag1 @tag2)")
        self.tags_input.textChanged.connect(self._on_tags_changed)
        header.addWidget(self.tags_input)

        header.addStretch()
        layout.addLayout(header)

        # Main content: Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setObjectName("mainSplitter")
        self.splitter.setHandleWidth(8)

        # Left: file list + log
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_preview_for_file)
        left_layout.addWidget(self.file_list, 1)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("System logs will appear here...")
        left_layout.addWidget(self.log_output, 1)

        self.splitter.addWidget(left_widget)

        # Right: preview
        self.back_button = QPushButton("Show All Scenarios")
        self.back_button.setToolTip("Back to the full .feature preview")
        self.back_button.clicked.connect(self.show_overall_preview)
        self.back_button.setVisible(False)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        right_layout.addWidget(self.back_button, 0)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        right_layout.addWidget(self.preview, 1)

        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([350, 550])
        layout.addWidget(self.splitter, 3)

        # Footer
        self.footer = QFrame()
        self.footer.setObjectName("footerBar")
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(12, 6, 12, 6)

        self.lblSummary = QLabel()
        self.lblSummary.setObjectName("lblSummary")
        footer_layout.addWidget(self.lblSummary)
        footer_layout.addStretch()

        self.generate_button = QPushButton("Generate .feature")
        self.generate_button.clicked.connect(self.generate_feature_file)
        footer_layout.addWidget(self.generate_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_all)
        footer_layout.addWidget(self.reset_button)

        layout.addWidget(self.footer, 0)
        self.setLayout(layout)
        self._update_summary()

    # --- Métodos de Lógica ---

    def _update_summary(self):
        """Atualiza o rodapé com as estatísticas atuais."""
        self.lblSummary.setText(
            f"Folders: {self.folder_count} • Files: {self.file_count} • "
            f"Features: {self.feature_count} • Scenarios: {self.scenario_count}"
        )

    def _build_feature_file_content(self, scenarios_list):
        """Constrói o conteúdo de um arquivo .feature a partir de uma lista de cenários."""
        if not scenarios_list:
            return "No scenarios found."

        # Adiciona a tag do projeto (se houver)
        content = f"{self.project_key}\n" if self.project_key else ""
        
        # Adiciona a declaração ÚNICA de Feature
        content += "Feature: Testes automatizados gerados pela aplicação Hobgoblin\n\n"

        # Adiciona cada cenário com suas tags
        for scenario_text in scenarios_list:
            if self.tags:
                content += f"{self.tags}\n"
            content += f"{scenario_text}\n\n"
        
        return content.strip()

    def toggle_subfolders(self, state: int):
        self.include_subfolders = (state == Qt.Checked)
        self.log_output.append(f"[INFO] Include subfolders: {self.include_subfolders}")
        if self.folder:
            self.select_folder(self.folder) # Re-scan folder with new setting

    def select_folder(self, folder_path=None):
        """Seleciona uma pasta e inicia a varredura por arquivos .robot."""
        folder = folder_path or QFileDialog.getExistingDirectory(self, "Select folder with .robot files")
        if not folder:
            return

        self.reset_all(clear_inputs=False) # Limpa dados, mas mantém inputs
        self.folder = folder
        self.log_output.append(f"[INFO] Folder selected: {folder}")

        # Varre os arquivos
        robot_files = []
        if self.include_subfolders:
            for root, _, files in os.walk(folder):
                self.folder_count += 1
                for file in files:
                    if file.lower().endswith(".robot"):
                        robot_files.append(os.path.join(root, file))
        else:
            self.folder_count = 1
            for file in os.listdir(folder):
                if file.lower().endswith(".robot"):
                    robot_files.append(os.path.join(folder, file))

        # Processa os arquivos encontrados
        for full_path in robot_files:
            self._process_file(full_path)
            self.file_count += 1 # Conta apenas os arquivos .robot processados
        
        # Define a contagem de features (será 1 se houver cenários)
        self.feature_count = 1 if self.all_scenarios else 0
        
        self.show_overall_preview()

        self.log_output.append("\n[SUMMARY]")
        self.log_output.append(f"- Total .robot files found: {self.file_count}")
        self.log_output.append(f"- Total Scenarios extracted: {self.scenario_count}\n")
        self._update_summary()

    def _process_file(self, full_path):
        """Processa um único arquivo .robot para extrair cenários."""
        self.file_list.addItem(full_path)
        try:
            # USA A NOVA FUNÇÃO DO PARSER
            scenarios, stats = extract_scenarios_from_robot_file(full_path)
            if scenarios:
                self.all_scenarios.extend(scenarios)
                self.scenario_count += stats["scenarios"]
                self.log_output.append(
                    f"[OK] {os.path.basename(full_path)} → {stats['scenarios']} Scenario(s) found"
                )
            else:
                self.log_output.append(f"[INFO] No scenarios found in {os.path.basename(full_path)}")
        except Exception as e:
            self.log_output.append(f"[ERROR] Failed to parse {full_path}: {e}")

    def show_preview_for_file(self, item):
        """Mostra o preview de um único arquivo selecionado na lista."""
        file_path = item.text()
        try:
            scenarios, _ = extract_scenarios_from_robot_file(file_path)
            preview_text = self._build_feature_file_content(scenarios)
        except Exception as e:
            preview_text = f"[ERROR] Failed to parse {file_path}: {e}"
        
        self.preview.setPlainText(preview_text)
        self.back_button.setVisible(True)

    def show_overall_preview(self):
        """Mostra o preview com todos os cenários encontrados."""
        self.file_list.clearSelection()
        preview_text = self._build_feature_file_content(self.all_scenarios)
        self.preview.setPlainText(preview_text)
        self.back_button.setVisible(False)

    def _on_project_changed(self, text):
        self.project_key = text.strip()
        self.show_overall_preview()

    def _on_tags_changed(self, text):
        self.tags = text.strip()
        self.show_overall_preview()

    def reset_all(self, clear_inputs=True):
        """Reseta o estado da aplicação."""
        self.file_list.clear()
        self.preview.clear()
        self.log_output.clear()
        self.folder = None
        self.all_scenarios.clear()
        if clear_inputs:
            self.project_input.setText("@PBC14TEST")
            self.tags_input.clear()
        self.folder_count = 0
        self.file_count = 0
        self.feature_count = 0
        self.scenario_count = 0
        self._update_summary()
        self.log_output.append("[INFO] Application reset.")

    def generate_feature_file(self):
        """Gera e salva o arquivo .feature final."""
        if not self.all_scenarios:
            QMessageBox.warning(self, "Warning", "No scenarios found to generate .feature file!")
            return

        # Gera o conteúdo final usando a função centralizada
        final_content = self._build_feature_file_content(self.all_scenarios)
        
        # Pede confirmação se os campos estiverem vazios
        if not self.project_key or not self.tags:
            reply = QMessageBox.question(
                self, "Attention", "Project or Tags field is empty. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                self.log_output.append("[INFO] File generation cancelled by user.")
                return
        
        # Salva o arquivo
        default_name = os.path.join(self.folder or os.getcwd(), "xray_generated.feature")
        output_path, _ = QFileDialog.getSaveFileName(self, "Save .feature File", default_name, "Feature File (*.feature)")
        
        if not output_path:
            self.log_output.append("[INFO] File save cancelled by user.")
            return

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            
            QMessageBox.information(self, "Success", f"File saved successfully at:\n{output_path}")
            self.log_output.append(f"[OK] .feature file generated at {output_path}")

            # Lógica para abrir no explorador e perguntar sobre a criação de teste no Xray...
            # (O resto do seu código a partir daqui pode ser mantido como estava)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
            self.log_output.append(f"[ERROR] Failed to save file: {e}")