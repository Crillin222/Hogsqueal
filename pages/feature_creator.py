# pages/feature_creator.py - VERSÃO ESTÁVEL (SEM DESTAQUE)

import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QTextEdit, QSplitter, QLabel, QFrame, QMessageBox, QFileDialog, QStackedWidget
)
from PySide6.QtCore import Qt

from services.file_service import find_robot_files
from services.feature_service import (
    process_robot_files, build_feature_content, save_feature_file
)

class FeatureCreatorPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.scenarios_data = []
        self.folder_path = None
        self.robot_files_found = []
        self.positions_map = {} # O serviço retorna, mas não usamos aqui.
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QHBoxLayout(); header.setContentsMargins(0, 0, 0, 0); header.setSpacing(8)
        self.folder_button = QPushButton("Select Folder"); self.folder_button.clicked.connect(self.run_scan_process)
        header.addWidget(self.folder_button)
        self.subfolders_checkbox = QPushButton("Include subfolders"); self.subfolders_checkbox.setObjectName("btnSubfolders"); self.subfolders_checkbox.setCheckable(True); self.subfolders_checkbox.setChecked(False); self.subfolders_checkbox.setToolTip("Toggle subfolder inclusion")
        header.addWidget(self.subfolders_checkbox)
        self.project_input = QLineEdit(); self.project_input.setPlaceholderText("Project (@KEYDOTESTE)"); self.project_input.setText("@PBC14TEST"); self.project_input.textChanged.connect(self.update_previews)
        header.addWidget(self.project_input)
        self.tags_input = QLineEdit(); self.tags_input.setPlaceholderText("Global Tags (@tag1 @tag2)"); self.tags_input.textChanged.connect(self.update_previews)
        header.addWidget(self.tags_input)
        header.addStretch(); layout.addLayout(header)
        self.splitter = QSplitter(Qt.Horizontal); self.splitter.setObjectName("mainSplitter"); self.splitter.setHandleWidth(8)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget); left_layout.setContentsMargins(0, 0, 0, 0); left_layout.setSpacing(6)
        view_toggle_layout = QHBoxLayout()
        self.view_toggle_button = QPushButton("Switch to File View"); self.view_toggle_button.clicked.connect(self.toggle_left_view)
        view_toggle_layout.addWidget(self.view_toggle_button)
        left_layout.addLayout(view_toggle_layout)
        self.left_stack = QStackedWidget()
        self.scenario_list = QListWidget()
        self.file_list = QListWidget()
        self.left_stack.addWidget(self.scenario_list)
        self.left_stack.addWidget(self.file_list)
        left_layout.addWidget(self.left_stack)
        rename_buttons_layout = QHBoxLayout()
        self.rename_by_file_button = QPushButton("Rename with Filename"); self.rename_by_file_button.clicked.connect(self.rename_scenario_by_filename)
        self.rename_by_test_case_button = QPushButton("Rename with Test Case"); self.rename_by_test_case_button.clicked.connect(self.rename_scenario_by_test_case)
        rename_buttons_layout.addWidget(self.rename_by_file_button)
        rename_buttons_layout.addWidget(self.rename_by_test_case_button)
        left_layout.addLayout(rename_buttons_layout)
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True); self.log_output.setPlaceholderText("System logs will appear here...")
        left_layout.addWidget(self.log_output, 1)
        self.splitter.addWidget(left_widget)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget); right_layout.setContentsMargins(0, 0, 0, 0); right_layout.setSpacing(6)
        self.preview = QTextEdit()
        right_layout.addWidget(self.preview, 1)
        self.splitter.addWidget(right_widget); self.splitter.setSizes([400, 500])
        layout.addWidget(self.splitter, 3)
        footer = QFrame(); footer.setObjectName("footerBar")
        footer_layout = QHBoxLayout(footer); footer_layout.setContentsMargins(12, 6, 12, 6)
        self.lblSummary = QLabel(); self.lblSummary.setObjectName("lblSummary")
        footer_layout.addWidget(self.lblSummary)
        footer_layout.addStretch()
        self.generate_button = QPushButton("Generate .feature"); self.generate_button.clicked.connect(self.generate_feature_file)
        footer_layout.addWidget(self.generate_button)
        self.reset_button = QPushButton("Reset"); self.reset_button.clicked.connect(self.reset_all)
        footer_layout.addWidget(self.reset_button)
        layout.addWidget(footer, 0); self.setLayout(layout); self.update_summary()

    def update_previews(self):
        project_key = self.project_input.text().strip()
        tags = self.tags_input.text().strip()
        # A função de serviço agora retorna duas coisas, mas só usamos a primeira
        content, self.positions_map = build_feature_content(self.scenarios_data, project_key, tags)
        self.preview.setPlainText(content)

    def run_scan_process(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder with .robot files")
        if not folder: return
        self.reset_all(clear_inputs=False)
        self.folder_path = folder
        self.log_output.append(f"[INFO] Folder selected: {self.folder_path}")
        try:
            self.robot_files_found = find_robot_files(self.folder_path, self.subfolders_checkbox.isChecked())
            self.scenarios_data, stats = process_robot_files(self.robot_files_found)
            self.populate_scenario_list()
            self.file_list.clear()
            self.file_list.addItems(self.robot_files_found)
            self.update_previews()
            self.log_output.append(f"\n[SUMMARY]\n- .robot files found: {len(self.robot_files_found)}\n- Scenarios extracted: {stats['scenarios_extracted']}\n")
            self.update_summary(stats)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            self.log_output.append(f"[ERROR] An unexpected error occurred: {e}")

    def populate_scenario_list(self):
        self.scenario_list.clear()
        for scenario in self.scenarios_data:
            display_text = f"{scenario['name']}  ({scenario['source_file']})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, scenario['id'])
            self.scenario_list.addItem(item)
            
    def _rename_selected_scenario(self, source_key: str):
        selected_items = self.scenario_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a scenario from the list first.")
            return

        selected_id = selected_items[0].data(Qt.UserRole)
        for scenario in self.scenarios_data:
            if scenario['id'] == selected_id:
                new_name_source = scenario.get(source_key, "Unknown")
                new_name = os.path.splitext(new_name_source)[0] if source_key == "source_file" else new_name_source
                lines = scenario['text'].split('\n')
                first_line = lines[0]
                keyword_match = re.match(r"^(.*?:)", first_line)
                if keyword_match:
                    keyword = keyword_match.group(1)
                    lines[0] = f"{keyword} {new_name}"
                    scenario['text'] = '\n'.join(lines)
                    scenario['name'] = new_name
                self.log_output.append(f"[INFO] Renamed scenario '{selected_id[:8]}' to '{new_name}'.")
                break
        
        self.populate_scenario_list()
        # Mantém o item renomeado selecionado na lista
        for i in range(self.scenario_list.count()):
            if self.scenario_list.item(i).data(Qt.UserRole) == selected_id:
                self.scenario_list.setCurrentRow(i)
                break
        self.update_previews()

    def rename_scenario_by_filename(self): self._rename_selected_scenario("source_file")
    def rename_scenario_by_test_case(self): self._rename_selected_scenario("robot_test_case")

    def generate_feature_file(self):
        if not self.scenarios_data:
            QMessageBox.warning(self, "Warning", "No scenarios found!")
            return
        final_content = self.preview.toPlainText()
        default_name = os.path.join(self.folder_path or os.getcwd(), "xray_generated.feature")
        output_path, _ = QFileDialog.getSaveFileName(self, "Save .feature File", default_name, "Feature File (*.feature)")
        if not output_path:
            self.log_output.append("[INFO] File save cancelled.")
            return
        try:
            save_feature_file(output_path, final_content)
            QMessageBox.information(self, "Success", f"File saved successfully at:\n{output_path}")
            self.log_output.append(f"[OK] .feature file generated at {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
            self.log_output.append(f"[ERROR] Failed to save file: {e}")

    def update_summary(self, stats: dict = None):
        if stats:
            self.lblSummary.setText(f"Files: {stats.get('files_processed', 0)} • Scenarios: {stats.get('scenarios_extracted', 0)}")
        else:
            self.lblSummary.setText("Files: 0 • Scenarios: 0")
            
    def toggle_left_view(self):
        current_index = self.left_stack.currentIndex()
        if current_index == 0:
            self.left_stack.setCurrentIndex(1)
            self.view_toggle_button.setText("Switch to Scenario View")
        else:
            self.left_stack.setCurrentIndex(0)
            self.view_toggle_button.setText("Switch to File View")

    def reset_all(self, clear_inputs=True):
        self.scenario_list.clear()
        self.file_list.clear()
        self.preview.clear()
        self.log_output.clear()
        self.folder_path = None
        self.scenarios_data = []
        self.robot_files_found = []
        if clear_inputs:
            self.project_input.setText("@PBC14TEST")
            self.tags_input.clear()
        self.update_summary()
        self.log_output.append("[INFO] Application reset.")