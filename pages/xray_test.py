import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, QButtonGroup, QStackedWidget,
    QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QFileDialog, QMessageBox
)
from utils.login_config import save_login_config, load_login_config
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

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Login group
        login_group = QGroupBox("Jira/Xray Login")
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

        # File selection group
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

        # Create test button
        self.create_test_btn = QPushButton("Create Xray Test")
        self.create_test_btn.clicked.connect(self.create_xray_test)
        layout.addWidget(self.create_test_btn)

        # Output log
        self.xray_log = QTextEdit()
        self.xray_log.setReadOnly(True)
        self.xray_log.setPlaceholderText("Command output will appear here...")
        layout.addWidget(self.xray_log, 1)

        self.setLayout(layout)

    def select_feature_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .feature file", "", "Feature Files (*.feature)")
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

    def create_xray_test(self):
        self.save_login_config()

        if not self.feature_file_path.text():
            QMessageBox.warning(self, "Warning", "Select a .feature file to create the test.")
            return

        if self.radio_userpass.isChecked():
            user = self.user_field.text().strip()
            passwd = self.pass_field.text().strip()
            if not user or not passwd:
                QMessageBox.warning(self, "Warning", "Fill in Jira username and password.")
                return
            auth = f"-u {user}:{passwd}"
        else:
            token = self.token_field.text().strip()
            if not token:
                QMessageBox.warning(self, "Warning", "Fill in the Jira token.")
                return
            auth = f'-H "Authorization: Bearer {token}"'

        feature_file = self.feature_file_path.text()
        url = "https:///jerry.dieboldnixdorf.com/rest/raven/2.0/import/feature"
        cmd = f'curl -X POST {auth} -F "file=@{feature_file}" "{url}"'

        self.xray_log.append(f"[CMD] {cmd}")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            self.xray_log.append(result.stdout)
            if result.stderr:
                self.xray_log.append(f"[ERROR] {result.stderr}")
        except Exception as e:
            self.xray_log.append(f"[EXCEPTION] {e}")