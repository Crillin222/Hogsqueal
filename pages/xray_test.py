# pages/xray_test.py
import os
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, QButtonGroup, QStackedWidget,
    QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QFileDialog, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

from utils.login_config import save_login_config, load_login_config
from utils.runtime import resource_path
import resources_rc
resources_rc.qInitResources()


class XrayTestPage(QWidget):
    """
    Page for logging in and sending .feature files to Xray/Jira.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.login_config = {}
        self.init_ui()
        self.load_login_config()

    # --------------------------- UI ---------------------------

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

        # Stacked widget for login fields
        self.login_stack = QStackedWidget()

        # Page 0: Username and Password
        userpass_widget = QWidget()
        userpass_layout = QVBoxLayout(userpass_widget)
        self.user_field = QLineEdit()
        self.user_field.setPlaceholderText("Jira Username")
        self.pass_field = QLineEdit()
        self.pass_field.setPlaceholderText("Jira Password")
        self.pass_field.setEchoMode(QLineEdit.Password)
        userpass_layout.addWidget(self.user_field)
        userpass_layout.addWidget(self.pass_field)
        self.login_stack.addWidget(userpass_widget)

        # Page 1: Token
        token_widget = QWidget()
        token_layout = QVBoxLayout(token_widget)
        self.token_field = QLineEdit()
        self.token_field.setPlaceholderText("Jira Token")
        token_layout.addWidget(self.token_field)
        self.login_stack.addWidget(token_widget)

        login_layout.addWidget(self.login_stack)

        # Switch login fields based on selection
        self.radio_userpass.toggled.connect(
            lambda checked: self.login_stack.setCurrentIndex(0 if checked else 1)
        )
        self.radio_token.toggled.connect(
            lambda checked: self.login_stack.setCurrentIndex(1 if checked else 0)
        )
        self.login_stack.setCurrentIndex(0)

        layout.addWidget(login_group)

        # --- Target Project (Project Key) ---
        project_group = QGroupBox("Target Project")
        project_layout = QHBoxLayout(project_group)
        project_layout.setSpacing(8)
        lbl = QLabel("Project Key:")
        self.project_key_field = QLineEdit()
        self.project_key_field.setPlaceholderText("e.g., PBC14TEST")
        self.project_key_field.setText("PBC14TEST")  # default
        self.project_key_field.setClearButtonEnabled(True)
        self.project_key_field.setMinimumWidth(160)
        project_layout.addWidget(lbl)
        project_layout.addWidget(self.project_key_field)
        project_layout.addStretch()
        layout.addWidget(project_group)

        # --- File selection group ---
        file_group = QGroupBox(".feature file for test creation")
        file_layout = QHBoxLayout(file_group)
        self.feature_file_path = QLineEdit()
        self.feature_file_path.setPlaceholderText("Select a .feature file")
        self.feature_file_path.setReadOnly(True)
        file_layout.addWidget(self.feature_file_path)
        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.clicked.connect(self.select_feature_file)
        file_layout.addWidget(self.select_file_btn)
        layout.addWidget(file_group)

        # --- Row of action buttons: Create Xray Test + Create dummy ---
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)

        # Create test button (usa o arquivo selecionado)
        self.create_test_btn = QPushButton("Create Jira Test")
        self.create_test_btn.clicked.connect(self.create_xray_test)
        buttons_row.addWidget(self.create_test_btn)

        # Create dummy (usa sempre resources/dummy/dummy.feature)
        self.create_dummy_btn = QPushButton("Create dummy")
        self.create_dummy_btn.setObjectName("btnSecondary")  # estilização opcional no QSS
        self.create_dummy_btn.setToolTip(
            "Create a Test in Jira using resources/dummy/dummy.feature (project key from the field above)"
        )
        self.create_dummy_btn.clicked.connect(self.create_dummy_test)
        buttons_row.addWidget(self.create_dummy_btn)

        buttons_row.addStretch()
        layout.addLayout(buttons_row)

        # --- Output log ---
        self.xray_log = QTextEdit()
        self.xray_log.setReadOnly(True)
        self.xray_log.setPlaceholderText("Command output will appear here...")
        layout.addWidget(self.xray_log, 1)

        self.setLayout(layout)

    # --------------------------- Actions ---------------------------

    def select_feature_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select .feature file", "", "Feature Files (*.feature)"
        )
        if file_path:
            self.feature_file_path.setText(file_path)

    def save_login_config(self):
        config = {
            "login_type": "userpass" if self.radio_userpass.isChecked() else "token",
            "user": self.user_field.text() if self.radio_userpass.isChecked() else "",
            "token": self.token_field.text() if self.radio_token.isChecked() else ""
        }
        save_login_config(config)
        self.login_config = config

    def load_login_config(self):
        config = load_login_config()
        self.login_config = config
        if config.get("login_type") == "userpass":
            self.radio_userpass.setChecked(True)
            self.user_field.setText(config.get("user", ""))
            self.token_field.setText("")
        else:
            self.radio_token.setChecked(True)
            self.token_field.setText(config.get("token", ""))
            self.user_field.setText("")

    # --------------------------- Helpers ---------------------------

    def _build_auth_args(self):
        """
        Retorna (auth_cmd, auth_log) para usar no curl e no log (com redação).
        Mostra QMessageBox e retorna (None, None) se faltar credencial.
        """
        if self.radio_userpass.isChecked():
            user = self.user_field.text().strip()
            passwd = self.pass_field.text().strip()
            if not user or not passwd:
                QMessageBox.warning(self, "Warning", "Fill in Jira username and password.")
                return None, None
            return f'-u "{user}:{passwd}"', '-u "***:***"'
        else:
            token = self.token_field.text().strip()
            if not token:
                QMessageBox.warning(self, "Warning", "Fill in the Jira token.")
                return None, None
            return f'-H "Authorization: Bearer {token}"', '-H "Authorization: Bearer ***"'

    def _read_project_key(self) -> str | None:
        pk = self.project_key_field.text().strip().upper()
        if not pk:
            QMessageBox.warning(self, "Warning", "Please fill the Project Key (e.g., PBC14TEST).")
            return None
        return pk

    def _run_curl_import_feature(self, feature_file: str, project_key: str):
        """
        Executa o curl de import do Xray para um arquivo .feature específico,
        usando as credenciais configuradas e o projectKey na URL.
        """
        self.save_login_config()

        auth_cmd, auth_log = self._build_auth_args()
        if not auth_cmd:
            return  # faltou credencial; mensagem já exibida

        base_url = "https://jerry.dieboldnixdorf.com/rest/raven/2.0/import/feature"
        url = f"{base_url}?projectKey={project_key}"

        # Monta comando (Windows-friendly, com aspas)
        cmd = f'curl -X POST {auth_cmd} -F "file=@{feature_file}" "{url}"'
        cmd_for_log = f'curl -X POST {auth_log} -F "file=@{feature_file}" "{url}"'

        self.xray_log.append(f"[CMD] {cmd_for_log}")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                self.xray_log.append(result.stdout)
            if result.stderr:
                self.xray_log.append(f"[ERROR] {result.stderr}")

            if result.returncode == 0:
                QMessageBox.information(self, "Success", "Test created successfully in Jira/Xray.")
            else:
                QMessageBox.warning(
                    self, "Warning",
                    f"curl returned non-zero exit code ({result.returncode}). Check the log."
                )
        except Exception as e:
            self.xray_log.append(f"[EXCEPTION] {e}")
            QMessageBox.critical(self, "Error", f"Failed to run curl:\n{e}")

    # --------------------------- Core actions ---------------------------

    def create_xray_test(self):
        """
        Cria Test no Xray/Jira usando o .feature selecionado via UI
        e o Project Key informado no campo acima.
        """
        feature_file = self.feature_file_path.text().strip()
        if not feature_file:
            QMessageBox.warning(self, "Warning", "Select a .feature file to create the test.")
            return
        if not os.path.exists(feature_file):
            QMessageBox.critical(self, "Error", f"Selected file not found:\n{feature_file}")
            return

        project_key = self._read_project_key()
        if not project_key:
            return

        self._run_curl_import_feature(feature_file, project_key=project_key)


    def create_dummy_test(self):
        dummy_file = resource_path("resources/dummy/dummy.feature")
        if not os.path.exists(dummy_file):
            QMessageBox.critical(
                self, "Error",
                f"Dummy file not found:\n{dummy_file}\n\n"
                "Check if the file exists and the working directory is correct."
            )
            return

        project_key = self._read_project_key()
        if not project_key:
            return

        self._run_curl_import_feature(dummy_file, project_key=project_key)
