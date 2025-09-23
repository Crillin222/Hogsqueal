import os
import sys
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget,
    QTextEdit, QSplitter, QLabel, QFrame, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from core.parser import parse_robot_file
import resources_rc
resources_rc.qInitResources()

class FeatureCreatorPage(QWidget):
    """
    Page for scanning .robot files, extracting features, and generating .feature files.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # State variables (INICIALIZE ANTES DE init_ui)
        self.include_subfolders = False
        self.folder = None
        self.all_features = []
        self.project_key = ""
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
        self.project_input.setText("@PBC14TEST")
        self.project_input.textChanged.connect(self._on_project_changed)
        header.addWidget(self.project_input)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (@tag1 @tag2)")
        self.tags_input.textChanged.connect(self._on_tags_changed)
        header.addWidget(self.tags_input)

        header.addStretch()
        layout.addLayout(header)

        # Main content: Splitter (left: files+log, right: preview)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setObjectName("mainSplitter")
        self.splitter.setHandleWidth(8)

        # Left: file list + log
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_preview)
        self.file_list.setSelectionMode(QListWidget.SingleSelection)
        left_layout.addWidget(self.file_list, 1)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("System logs will appear here...")
        left_layout.addWidget(self.log_output, 1)

        self.splitter.addWidget(left_widget)

        # Right: preview
        self.back_button = QPushButton("Show All Features")
        self.back_button.setToolTip("Back to the combined .feature preview")
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

        # Footer: summary + generate/reset buttons
        self.footer = QFrame()
        self.footer.setObjectName("footerBar")
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(12, 6, 12, 6)
        footer_layout.setSpacing(8)

        self.lblSummary = QLabel()
        self.lblSummary.setObjectName("lblSummary")
        footer_layout.addWidget(self.lblSummary)
        footer_layout.addStretch()

        self.generate_button = QPushButton("Generate .feature")
        self.generate_button.clicked.connect(self.generate_feature)
        footer_layout.addWidget(self.generate_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Clear everything and reset")
        self.reset_button.clicked.connect(self.reset_all)
        footer_layout.addWidget(self.reset_button)

        layout.addWidget(self.footer, 0)
        self.setLayout(layout)
        self._update_summary()

    # --- Logic methods below ---

    def _update_summary(self):
        self.lblSummary.setText(
            f"Folders: {self.folder_count} • Files: {self.file_count} • "
            f"Features: {self.feature_count} • Scenarios: {self.scenario_count}"
        )

    def toggle_subfolders(self, state: int):
        self.include_subfolders = (state == Qt.Checked)
        self.log_output.append(f"[INFO] Include subfolders: {self.include_subfolders}")

    def _apply_project_and_tags(self, features):
        features_with_project_and_tags = []
        for feature in features:
            lines = feature.splitlines()
            new_lines = []
            if self.project_key:
                new_lines.append(self.project_key)
            for line in lines:
                if line.strip().lower().startswith("scenario") and self.tags:
                    new_lines.append(self.tags)
                new_lines.append(line)
            features_with_project_and_tags.append("\n".join(new_lines))
        return features_with_project_and_tags

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder with .robot files")
        if folder:
            self.file_list.clear()
            self.folder = folder
            self.all_features.clear()
            self.back_button.setVisible(False)

            self.folder_count = 0
            self.file_count = 0
            self.feature_count = 0
            self.scenario_count = 0
            self._update_summary()

            self.log_output.append(f"[INFO] Folder selected: {folder}")

            if self.include_subfolders:
                for root, dirs, files in os.walk(folder):
                    self.folder_count += 1
                    for file in files:
                        self.file_count += 1
                        if file.lower().endswith(".robot"):
                            full_path = os.path.join(root, file)
                            self._process_file(full_path)
            else:
                self.folder_count = 1
                for file in os.listdir(folder):
                    self.file_count += 1
                    if file.lower().endswith(".robot"):
                        full_path = os.path.join(folder, file)
                        self._process_file(full_path)

            if self.all_features:
                preview_text = "\n\n---\n\n".join(self._apply_project_and_tags(self.all_features))
            else:
                preview_text = "No Feature blocks found in files."
            self.preview.setPlainText(preview_text)

            self.log_output.append("\n[SUMMARY]")
            self.log_output.append(f"- Total folders scanned: {self.folder_count}")
            self.log_output.append(f"- Total .robot files: {self.file_count}")
            self.log_output.append(f"- Total Features extracted: {self.feature_count}")
            self.log_output.append(f"- Total Scenarios extracted: {self.scenario_count}\n")

            self._update_summary()

    def _process_file(self, full_path):
        self.file_list.addItem(full_path)
        try:
            features, stats = parse_robot_file(full_path)
            if features:
                self.all_features.extend(features)
                self.feature_count += stats["features"]
                self.scenario_count += stats["scenarios"]
                self.log_output.append(
                    f"[OK] {os.path.basename(full_path)} → "
                    f"{stats['features']} Feature(s), {stats['scenarios']} Scenario(s)"
                )
            else:
                self.log_output.append(f"[WARN] No Feature found in {full_path}")
        except Exception as e:
            self.log_output.append(f"[ERROR] Failed to parse {full_path}: {e}")

    def show_preview(self, item):
        file_path = item.text()
        try:
            features, _ = parse_robot_file(file_path)
            if features:
                preview_text = "\n\n---\n\n".join(self._apply_project_and_tags(features))
            else:
                preview_text = "No Feature blocks found in this file."
        except Exception as e:
            preview_text = f"[ERROR] Failed to parse {file_path}: {e}"
        self.preview.setPlainText(preview_text)
        self.back_button.setVisible(True)

    def show_overall_preview(self):
        self.file_list.clearSelection()
        if self.all_features:
            preview_text = "\n\n---\n\n".join(self._apply_project_and_tags(self.all_features))
        else:
            preview_text = "No Feature blocks found in files."
        self.preview.setPlainText(preview_text)
        self.back_button.setVisible(False)

    def _on_project_changed(self, text):
        self.project_key = text.strip()

    def _on_tags_changed(self, text):
        self.tags = text.strip()

    def reset_all(self):
        self.file_list.clear()
        self.preview.clear()
        self.log_output.clear()
        self.folder = None
        self.all_features.clear()
        self.project_input.clear()
        self.tags_input.clear()
        self.project_key = ""
        self.tags = ""
        self.folder_count = 0
        self.file_count = 0
        self.feature_count = 0
        self.scenario_count = 0
        self._update_summary()
        self.log_output.append("[INFO] Application reset.")

    def generate_feature(self):
        if not self.all_features:
            QMessageBox.warning(self, "Warning", "No content to generate .feature!")
            return

        if not self.project_key or not self.tags:
            msg = "Are you sure you want to generate the file without "
            if not self.project_key and not self.tags:
                msg += "project and tags?"
            elif not self.project_key:
                msg += "project?"
            else:
                msg += "tags?"
            reply = QMessageBox.question(
                self, "Attention", msg,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                self.log_output.append("[INFO] File generation cancelled by user.")
                return

        output_path = os.path.join(self.folder, "combined.feature")
        try:
            features_with_project_and_tags = self._apply_project_and_tags(self.all_features)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(features_with_project_and_tags))

            QMessageBox.information(self, "Success", f"File saved at:\n{output_path}")
            self.log_output.append(f"[OK] .feature file generated at {output_path}")

            # Open in file explorer
            if sys.platform == "win32":
                output_path_win = os.path.normpath(output_path)
                subprocess.Popen(f'explorer /select,"{output_path_win}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", output_path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(output_path)])

            # Integration with Xray page
            reply = QMessageBox.question(
                self,
                "Create Xray Test",
                "Do you want to create Xray tests using this file now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                # Switch to Xray tab and set file
                self.main_window.tabs.setCurrentWidget(self.main_window.xray_test_page)
                self.main_window.xray_test_page.feature_file_path.setText(output_path)
                # Try to auto-run if login exists
                self.main_window.xray_test_page.load_login_config()
                config = self.main_window.xray_test_page.login_config
                login_type = config.get("login_type")
                user_ok = bool(config.get("user")) if login_type == "userpass" else False
                token_ok = bool(config.get("token")) if login_type == "token" else False
                if (login_type == "userpass" and user_ok) or (login_type == "token" and token_ok):
                    self.main_window.xray_test_page.create_xray_test()
                # Otherwise, just leave the file pre-selected

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
            self.log_output.append(f"[ERROR] Failed to save file: {e}")