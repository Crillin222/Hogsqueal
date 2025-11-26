# pages/xray_test.py - VERSÃO CORRIGIDA COM QTextBrowser

import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, QButtonGroup, QStackedWidget,
    QLineEdit, QPushButton, QTextBrowser, QHBoxLayout, QFileDialog, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

from services.jira_service import import_feature_to_xray, update_issue_description, JIRA_BASE_URL
from utils.login_config import save_login_config, load_login_config
import resources_rc

resources_rc.qInitResources()

JIRA_DUMMY_TEST_KEY = 'PBC14TEST-54285'

class XrayTestPage(QWidget):
    """
    Page for logging in and sending .feature files to Xray/Jira with Rich Text Output.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.login_config = {}
        self.init_ui()
        self.load_login_config_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # --- Login group ---
        login_group = QGroupBox("Jira Login")
        login_layout = QVBoxLayout(login_group)

        self.radio_userpass = QRadioButton("Username and Password")
        self.radio_token = QRadioButton("Jira Token")
        self.radio_userpass.setChecked(True)
        login_layout.addWidget(self.radio_userpass)
        login_layout.addWidget(self.radio_token)

        self.login_method_group = QButtonGroup()
        self.login_method_group.addButton(self.radio_userpass)
        self.login_method_group.addButton(self.radio_token)

        self.login_stack = QStackedWidget()

        # Page 0: User/Pass
        userpass_widget = QWidget()
        userpass_layout = QVBoxLayout(userpass_widget)
        self.user_field = QLineEdit(); self.user_field.setPlaceholderText("Jira Username")
        self.pass_field = QLineEdit(); self.pass_field.setPlaceholderText("Jira Password"); self.pass_field.setEchoMode(QLineEdit.Password)
        userpass_layout.addWidget(self.user_field); userpass_layout.addWidget(self.pass_field)
        self.login_stack.addWidget(userpass_widget)

        # Page 1: Token
        token_widget = QWidget()
        token_layout = QVBoxLayout(token_widget)
        self.token_field = QLineEdit(); self.token_field.setPlaceholderText("Jira Token")
        token_layout.addWidget(self.token_field)
        self.login_stack.addWidget(token_widget)

        login_layout.addWidget(self.login_stack)
        self.radio_userpass.toggled.connect(lambda c: self.login_stack.setCurrentIndex(0 if c else 1))
        self.radio_token.toggled.connect(lambda c: self.login_stack.setCurrentIndex(1 if c else 0))
        layout.addWidget(login_group)

        # --- Project ---
        project_group = QGroupBox("Target Project")
        project_layout = QHBoxLayout(project_group)
        self.project_key_field = QLineEdit(); self.project_key_field.setPlaceholderText("e.g., PBC14TEST"); self.project_key_field.setText("PBC14TEST")
        project_layout.addWidget(QLabel("Project Key:")); project_layout.addWidget(self.project_key_field)
        layout.addWidget(project_group)

        # --- File ---
        file_group = QGroupBox(".feature file for test creation")
        file_layout = QHBoxLayout(file_group)
        self.feature_file_path = QLineEdit(); self.feature_file_path.setReadOnly(True); self.feature_file_path.setPlaceholderText("Select a .feature file")
        self.select_file_btn = QPushButton("Select File"); self.select_file_btn.clicked.connect(self.select_feature_file)
        file_layout.addWidget(self.feature_file_path); file_layout.addWidget(self.select_file_btn)
        layout.addWidget(file_group)

        # --- Buttons ---
        buttons_row = QHBoxLayout()
        self.create_test_btn = QPushButton("Create Jira Test"); self.create_test_btn.clicked.connect(self.create_xray_test)
        self.create_dummy_btn = QPushButton("Test Application Connection"); self.create_dummy_btn.clicked.connect(self.create_dummy_test)
        buttons_row.addWidget(self.create_test_btn); buttons_row.addWidget(self.create_dummy_btn)
        layout.addLayout(buttons_row)

        # --- Output Log (CORRIGIDO PARA QTextBrowser) ---
        self.xray_log = QTextBrowser()  # ### MUDANÇA AQUI ###
        self.xray_log.setOpenExternalLinks(True) # Agora funciona!
        self.xray_log.setPlaceholderText("Results will appear here...")
        layout.addWidget(self.xray_log, 1)

        self.setLayout(layout)

    # --------------------------- Logic ---------------------------

    def select_feature_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .feature file", "", "Feature Files (*.feature)")
        if file_path: self.feature_file_path.setText(file_path)

    def save_current_login(self):
        self.login_config = {
            "login_type": "userpass" if self.radio_userpass.isChecked() else "token",
            "user": self.user_field.text().strip(),
            "token": self.pass_field.text().strip() if self.radio_userpass.isChecked() else self.token_field.text().strip()
        }
        save_login_config(self.login_config)

    def load_login_config_data(self):
        config = load_login_config()
        self.login_config = config
        if config.get("login_type") == "userpass":
            self.radio_userpass.setChecked(True)
            self.user_field.setText(config.get("user", ""))
            self.pass_field.setText(config.get("token", ""))
        else:
            self.radio_token.setChecked(True)
            self.token_field.setText(config.get("token", ""))

    def log_html(self, html_content):
        self.xray_log.append(html_content)
        sb = self.xray_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    # --- AÇÕES PRINCIPAIS ---

    def create_xray_test(self):
        feature_file = self.feature_file_path.text().strip()
        project_key = self.project_key_field.text().strip().upper()

        if not feature_file or not os.path.exists(feature_file):
            QMessageBox.warning(self, "Warning", "Please select a valid .feature file.")
            return
        if not project_key:
            QMessageBox.warning(self, "Warning", "Please enter a Project Key.")
            return

        self.save_current_login()
        self.xray_log.clear()
        self.log_html(f"<b>🚀 Starting Xray Import...</b><br>File: <i>{os.path.basename(feature_file)}</i><br>Project: {project_key}<br><hr>")

        try:
            result_list = import_feature_to_xray(feature_file, project_key, self.login_config)
            
            success_html = "<h3 style='color: #2ecc71;'>✅ Import Successful!</h3>"
            success_html += "<p>The following tests were created/updated:</p><ul>"
            
            for item in result_list:
                key = item.get('key') or item.get('test') or item.get('id')
                if key:
                    link = f"{JIRA_BASE_URL}/browse/{key}"
                    success_html += f"<li><b><a href='{link}' style='color: #3498db;'>{key}</a></b> - Test Updated/Created</li>"
                else:
                    success_html += f"<li>{item}</li>"
            
            success_html += "</ul>"
            self.log_html(success_html)
            QMessageBox.information(self, "Success", "Tests imported successfully!")

        except Exception as e:
            error_html = f"<h3 style='color: #e74c3c;'>❌ Error</h3><p>{str(e)}</p>"
            self.log_html(error_html)
            QMessageBox.critical(self, "Error", f"Failed to import tests:\n{e}")

    def create_dummy_test(self):
        self.save_current_login()
        self.xray_log.clear()
        self.log_html(f"<b>📡 Testing Connection...</b><br>Target Issue: {JIRA_DUMMY_TEST_KEY}<br><hr>")

        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        description = f"Connection verification test executed successfully via Hobgoblin.\nTimestamp: {timestamp}"

        try:
            update_issue_description(JIRA_DUMMY_TEST_KEY, description, self.login_config)
            
            link = f"{JIRA_BASE_URL}/browse/{JIRA_DUMMY_TEST_KEY}"
            msg = (f"<h3 style='color: #2ecc71;'>✅ Connection Verified!</h3>"
                   f"<p>Issue <b><a href='{link}' style='color: #3498db;'>{JIRA_DUMMY_TEST_KEY}</a></b> updated successfully.</p>")
            self.log_html(msg)
            QMessageBox.information(self, "Success", "Connection verified!")

        except Exception as e:
            error_html = f"<h3 style='color: #e74c3c;'>❌ Connection Failed</h3><p>{str(e)}</p>"
            self.log_html(error_html)
            QMessageBox.critical(self, "Error", f"Connection failed:\n{e}")