# pages/feature_creator.py - VERSÃO FINAL (Global Tags Corrigido + Project Key Removido)

import os
import re
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QTextEdit, QSplitter, QLabel, QFrame, QMessageBox, QFileDialog, QListWidget, QListWidgetItem, QStackedWidget,
    QStylePainter, QStyleOptionButton, QStyle, QAbstractItemView, QHeaderView, QCheckBox
)
from PySide6.QtCore import Qt, QSize

from services.file_service import find_robot_files
from services.feature_service import (
    process_robot_files, build_feature_content, save_feature_file
)

class VerticalButton(QPushButton):
    def paintEvent(self, event):
        painter = QStylePainter(self); option = QStyleOptionButton(); self.initStyleOption(option)
        painter.drawControl(QStyle.CE_PushButtonBevel, option); painter.save()
        painter.translate(self.width(), 0); painter.rotate(90)
        text_rect = self.rect().transposed(); painter.drawText(text_rect, Qt.AlignCenter, self.text())
        painter.restore()
    def sizeHint(self):
        hint = super().sizeHint(); return QSize(hint.height(), hint.width())

class FeatureCreatorPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window; self.scenarios_data = []; self.folder_path = None
        self.robot_files_found = []; self.positions_map = {}
        self.init_ui()

    def init_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(10, 10, 10, 10); page_layout.setSpacing(8)

        header = QHBoxLayout()
        self.folder_button = QPushButton("Select Folder"); self.folder_button.clicked.connect(self.run_scan_process)
        header.addWidget(self.folder_button)
        self.subfolders_checkbox = QPushButton("Include subfolders"); self.subfolders_checkbox.setObjectName("btnSubfolders"); self.subfolders_checkbox.setCheckable(True); self.subfolders_checkbox.setChecked(False); self.subfolders_checkbox.setToolTip("Toggle subfolder inclusion")
        header.addWidget(self.subfolders_checkbox)
        header.addStretch()
        page_layout.addLayout(header)

        self.splitter = QSplitter(Qt.Horizontal); self.splitter.setObjectName("mainSplitter"); self.splitter.setHandleWidth(8)
        
        tools_container = QWidget()
        tools_layout = QHBoxLayout(tools_container); tools_layout.setContentsMargins(0,0,0,0); tools_layout.setSpacing(5)

        tool_nav_panel = QWidget(); tool_nav_layout = QVBoxLayout(tool_nav_panel)
        self.btn_tags_tool = VerticalButton("Tags"); self.btn_tags_tool.setCheckable(True)
        self.btn_rename_tool = VerticalButton("Rename"); self.btn_rename_tool.setCheckable(True)
        self.btn_folders_tool = VerticalButton("Folders"); self.btn_folders_tool.setCheckable(True)
        self.btn_tags_tool.clicked.connect(lambda: self.change_tool_page(0))
        self.btn_rename_tool.clicked.connect(lambda: self.change_tool_page(1))
        self.btn_folders_tool.clicked.connect(lambda: self.change_tool_page(2))
        tool_nav_layout.addWidget(self.btn_tags_tool); tool_nav_layout.addWidget(self.btn_rename_tool); tool_nav_layout.addWidget(self.btn_folders_tool)
        tool_nav_layout.addStretch()
        tools_layout.addWidget(tool_nav_panel)

        self.scenario_table = QTableWidget()
        self.scenario_table.setColumnCount(3); self.scenario_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.scenario_table.cellChanged.connect(self.on_tags_changed)
        
        self.master_checkbox = QCheckBox()
        self.master_checkbox.setToolTip("Select / Deselect All")
        self.master_checkbox.toggled.connect(self.toggle_all_checkboxes)
        header_view = self.scenario_table.horizontalHeader()
        header_view.setStretchLastSection(False) 
        header_layout = QHBoxLayout(header_view)
        header_layout.addStretch()
        header_layout.insertWidget(0, self.master_checkbox, 0, Qt.AlignmentFlag.AlignLeft)
        header_layout.setContentsMargins(4,0,0,0) 
        
        self.scenario_table.setHorizontalHeaderLabels(["", "Scenario Name", "Additional Tags"])

        self.tool_stack = QStackedWidget()
        tools_layout.addWidget(self.tool_stack)

        tags_tool_panel = QWidget(); tags_tool_layout = QVBoxLayout(tags_tool_panel)
        tags_inputs_layout = QHBoxLayout()
        
        # ### ALTERADO: Removido Project Input ###
        self.tags_input = QLineEdit(); self.tags_input.setPlaceholderText("Global Tags (@tag1)"); self.tags_input.textChanged.connect(self.update_previews)
        tags_inputs_layout.addWidget(self.tags_input)
        
        tags_tool_layout.addLayout(tags_inputs_layout)
        tags_tool_layout.addWidget(QLabel("Master Tag Control (Enable/Disable):"))
        self.master_tags_list = QListWidget(); self.master_tags_list.itemChanged.connect(self.update_previews)
        tags_tool_layout.addWidget(self.master_tags_list, 1)
        tags_tool_layout.addWidget(QLabel("Scenarios (Add specific tags below):"))

        rename_tool_panel = QWidget(); self.rename_tool_layout = QVBoxLayout(rename_tool_panel)
        self.rename_tool_layout.addWidget(QLabel("Select scenarios to rename:"))
        rename_buttons_container = QWidget()
        rename_buttons_layout = QHBoxLayout(rename_buttons_container); rename_buttons_layout.setContentsMargins(0,0,0,0)
        self.rename_by_file_button = QPushButton("Rename Checked with Filename"); self.rename_by_file_button.clicked.connect(self.rename_scenario_by_filename)
        self.rename_by_test_case_button = QPushButton("Rename Checked with Test Case"); self.rename_by_test_case_button.clicked.connect(self.rename_scenario_by_test_case)
        rename_buttons_layout.addStretch(1); rename_buttons_layout.addWidget(self.rename_by_file_button); rename_buttons_layout.addWidget(self.rename_by_test_case_button); rename_buttons_layout.addStretch(1)
        self.rename_tool_layout.addWidget(rename_buttons_container)

        folders_tool_panel = QWidget(); folders_tool_layout = QVBoxLayout(folders_tool_panel)
        self.file_list = QListWidget(); folders_tool_layout.addWidget(self.file_list)

        self.tool_stack.addWidget(tags_tool_panel); self.tool_stack.addWidget(rename_tool_panel); self.tool_stack.addWidget(folders_tool_panel)
        
        right_panel = QWidget(); right_layout = QVBoxLayout(right_panel); right_layout.setContentsMargins(0,0,0,0)
        self.preview = QTextEdit(); right_layout.addWidget(self.preview, 3)
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True); self.log_output.setPlaceholderText("System logs will appear here...")
        right_layout.addWidget(self.log_output, 1)

        self.splitter.addWidget(tools_container); self.splitter.addWidget(right_panel); self.splitter.setSizes([700, 500])
        page_layout.addWidget(self.splitter)

        self.footer = QFrame(); self.footer.setObjectName("footerBar"); self.footer.setMaximumHeight(40)
        footer_layout = QHBoxLayout(self.footer); footer_layout.setContentsMargins(12, 6, 12, 6)
        self.lblSummary = QLabel(); self.lblSummary.setObjectName("lblSummary"); footer_layout.addWidget(self.lblSummary); footer_layout.addStretch()
        self.generate_button = QPushButton("Generate .feature"); self.generate_button.clicked.connect(self.generate_feature_file)
        footer_layout.addWidget(self.generate_button)
        self.reset_button = QPushButton("Reset"); self.reset_button.clicked.connect(self.reset_all)
        footer_layout.addWidget(self.reset_button)
        page_layout.addWidget(self.footer)
        
        self.change_tool_page(0)

    def change_tool_page(self, index: int):
        self.tool_stack.setCurrentIndex(index)
        
        normal_width, selected_width = 30, 40
        self.btn_tags_tool.setChecked(index == 0); self.btn_tags_tool.setFixedWidth(selected_width if index == 0 else normal_width)
        self.btn_rename_tool.setChecked(index == 1); self.btn_rename_tool.setFixedWidth(selected_width if index == 1 else normal_width)
        self.btn_folders_tool.setChecked(index == 2); self.btn_folders_tool.setFixedWidth(selected_width if index == 2 else normal_width)

        self.scenario_table.setColumnHidden(2, index != 0)
        # ### AJUSTE ###: Coluna 0 (Checkbox) só visível na aba Rename (index 1)
        self.scenario_table.setColumnHidden(0, index != 1)
        self.master_checkbox.setVisible(index == 1)

        if index == 0:
            self.tool_stack.widget(0).layout().addWidget(self.scenario_table, 1)
        elif index == 1:
            self.rename_tool_layout.insertWidget(1, self.scenario_table, 1)

    def populate_scenario_table(self):
        self.scenario_table.cellChanged.disconnect(self.on_tags_changed); self.scenario_table.setRowCount(0)
        for row, scenario in enumerate(self.scenarios_data):
            self.scenario_table.insertRow(row)
            
            check_item = QTableWidgetItem(); check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled); check_item.setCheckState(Qt.Unchecked)
            self.scenario_table.setItem(row, 0, check_item)

            name_item = QTableWidgetItem(f"{scenario['name']} ({scenario['source_file']})")
            name_item.setData(Qt.UserRole, scenario['id']); name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.scenario_table.setItem(row, 1, name_item)

            additional_tags_str = scenario.get('additional_tags', '')
            self.scenario_table.setItem(row, 2, QTableWidgetItem(additional_tags_str))

        self.scenario_table.resizeColumnsToContents()
        self.scenario_table.setColumnWidth(0, 30)
        self.scenario_table.cellChanged.connect(self.on_tags_changed)
        self.master_checkbox.setChecked(False)

    def on_tags_changed(self, row, column):
        if column != 2: return
        scenario_id = self.scenario_table.item(row, 1).data(Qt.UserRole)
        new_tags = self.scenario_table.item(row, column).text().strip()
        for scenario in self.scenarios_data:
            if scenario['id'] == scenario_id:
                scenario['additional_tags'] = new_tags; break
        self.update_previews()

    def toggle_all_checkboxes(self, checked: bool):
        state = Qt.Checked if checked else Qt.Unchecked
        for row in range(self.scenario_table.rowCount()):
            self.scenario_table.item(row, 0).setCheckState(state)

    def _rename_selected_scenario(self, source_key: str):
        renamed_count = 0
        for row in range(self.scenario_table.rowCount()):
            if self.scenario_table.item(row, 0).checkState() == Qt.Checked:
                scenario_id = self.scenario_table.item(row, 1).data(Qt.UserRole)
                for scenario in self.scenarios_data:
                    if scenario['id'] == scenario_id:
                        new_name_source = scenario.get(source_key, "Unknown")
                        new_name = os.path.splitext(new_name_source)[0] if source_key == 'source_file' else new_name_source
                        lines = scenario['text'].split('\n'); first_line = lines[0]
                        keyword_match = re.match(r"^(.*?:)", first_line)
                        if keyword_match:
                            keyword = keyword_match.group(1); lines[0] = f"{keyword} {new_name}"; scenario['text'] = '\n'.join(lines); scenario['name'] = new_name
                        renamed_count += 1
                        break
        if renamed_count == 0:
            QMessageBox.warning(self, "Warning", "No scenarios selected. Please check the boxes for the scenarios you want to rename.")
            return
        self.log_output.append(f"[INFO] Renamed {renamed_count} scenarios.")
        self.populate_scenario_table(); self.update_previews()
    
    def run_scan_process(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder with .robot files");
        if not folder: return
        self.reset_all(clear_inputs=False); self.folder_path = folder
        self.log_output.append(f"[INFO] Folder selected: {self.folder_path}")
        try:
            self.robot_files_found = find_robot_files(self.folder_path, self.subfolders_checkbox.isChecked())
            self.scenarios_data, stats = process_robot_files(self.robot_files_found)
            self.populate_master_tag_list(); self.populate_scenario_table(); self.file_list.clear(); self.file_list.addItems(self.robot_files_found)
            self.update_previews(); self.update_summary(stats)
            self.log_output.append(f"\n[SUMMARY]\n- .robot files found: {len(self.robot_files_found)}\n- Scenarios extracted: {stats['scenarios_extracted']}\n")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during scan: {e}"); self.log_output.append(f"[ERROR] Scan failed: {e}")
    def populate_master_tag_list(self):
        self.master_tags_list.itemChanged.disconnect(self.update_previews); self.master_tags_list.clear()
        unique_tags = set()
        for scenario in self.scenarios_data:
            detected = scenario.get('detected_tags', {})
            unique_tags.update(detected.get('force', [])); unique_tags.update(detected.get('case', []))
        for tag in sorted(list(unique_tags)):
            item = QListWidgetItem(tag); item.setFlags(item.flags() | Qt.ItemIsUserCheckable); item.setCheckState(Qt.Checked)
            self.master_tags_list.addItem(item)
        self.master_tags_list.itemChanged.connect(self.update_previews)
    def get_active_tags(self) -> List[str]:
        active_tags = [];
        for i in range(self.master_tags_list.count()):
            item = self.master_tags_list.item(i)
            if item.checkState() == Qt.Checked: active_tags.append(item.text())
        return active_tags
    def update_previews(self):
        active_tags = self.get_active_tags()
        
        # ### ATUALIZADO: Chamada sem o project_key ###
        content, self.positions_map = build_feature_content(
            self.scenarios_data, 
            self.tags_input.text().strip(), 
            active_tags
        )
        self.preview.setPlainText(content)

    def rename_scenario_by_filename(self): self._rename_selected_scenario("source_file")
    def rename_scenario_by_test_case(self): self._rename_selected_scenario("robot_test_case")
    def generate_feature_file(self):
        final_content = self.preview.toPlainText()
        if not final_content or "No scenarios found" in final_content: QMessageBox.warning(self, "Warning", "No scenarios to generate!"); return
        default_name = os.path.join(self.folder_path or os.getcwd(), "xray_generated.feature")
        output_path, _ = QFileDialog.getSaveFileName(self, "Save .feature File", default_name, "Feature File (*.feature)")
        if not output_path: return
        try: save_feature_file(output_path, final_content); QMessageBox.information(self, "Success", f"File saved at:\n{output_path}")
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
    def update_summary(self, stats: dict = None):
        if stats: self.lblSummary.setText(f"Files: {stats.get('files_processed', 0)} • Scenarios: {stats.get('scenarios_extracted', 0)}")
        else: self.lblSummary.setText("Files: 0 • Scenarios: 0")
    def reset_all(self, clear_inputs=True):
        self.master_tags_list.clear(); self.scenario_table.setRowCount(0); self.file_list.clear(); self.preview.clear(); self.log_output.clear()
        self.folder_path = None; self.scenarios_data = []; self.robot_files_found = []
        if clear_inputs: self.tags_input.clear() # Limpa tags, project input removido
        self.update_summary(); self.log_output.append("[INFO] Application reset.")