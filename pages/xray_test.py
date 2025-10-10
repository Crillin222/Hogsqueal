# -*- coding: utf-8 -*-

import os, tempfile, datetime
import subprocess
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, QButtonGroup, QStackedWidget,
    QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QFileDialog, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

from utils.login_config import save_login_config, load_login_config
from utils.runtime import resource_path
import resources_rc
resources_rc.qInitResources()


# --- Configuração Essencial para o Teste de Verificação ---
# Substitua 'PROJ-123' pela chave real do teste que você criou no Jira
# para ser o alvo da atualização do "dummy test".
JIRA_DUMMY_TEST_KEY = 'PBC14TEST-54285' 


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
        self.create_dummy_btn = QPushButton("Test Application Connection") # Nome alterado para clareza
        self.create_dummy_btn.setObjectName("btnSecondary")  # estilização opcional no QSS
        self.create_dummy_btn.setToolTip(
            f"Updates a specific test ({JIRA_DUMMY_TEST_KEY}) in Jira with the current timestamp to verify the connection."
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

    def _render_last_update_line(self) -> str:
        """Retorna timestamp no formato DD/MM/YYYY HH:MM (timezone local)."""
        now = datetime.datetime.now().astimezone()
        return now.strftime("%d/%m/%Y %H:%M")

    def _make_timestamped_copy(self, feature_path: str) -> str:
        """
        Gera uma cópia temporária do .feature substituindo {{LAST_UPDATE}} pelo timestamp.
        Se o placeholder não existir, a função não falha: cria cópia idêntica.
        Retorna o caminho da cópia (o chamador deve excluir depois).
        """
        with open(feature_path, "r", encoding="utf-8") as fh:
            text = fh.read()

        ts = self._render_last_update_line()
        new_text = text.replace("{{LAST_UPDATE}}", ts)

        dir_name = os.path.dirname(os.path.abspath(feature_path))
        fd, tmp_path = tempfile.mkstemp(prefix="tmp_dummy_", suffix=".feature", dir=dir_name, text=True)
        os.close(fd)
        with open(tmp_path, "w", encoding="utf-8", newline="\n") as out:
            out.write(new_text if new_text.endswith("\n") else new_text + "\n")
        return tmp_path

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
        Executa o curl de import do Xray para um arquivo .feature.
        """
        self.save_login_config()

        feature_for_upload = feature_file
        tmp_to_cleanup = None
        try:
            tmp_to_cleanup = self._make_timestamped_copy(feature_file)
            feature_for_upload = tmp_to_cleanup
            self.xray_log.append(f"[INFO] Using timestamped copy: {feature_for_upload}")
        except Exception as e:
            self.xray_log.append(f"[WARN] Could not render timestamped copy, using original. Details: {e}")

        auth_cmd, auth_log = self._build_auth_args()
        if not auth_cmd:
            if tmp_to_cleanup and os.path.exists(tmp_to_cleanup):
                try: os.remove(tmp_to_cleanup)
                except Exception: pass
            return

        base_url = "https://jerry.dieboldnixdorf.com/rest/raven/2.0/import/feature"
        url = f"{base_url}?projectKey={project_key}"

        cmd = f'curl -X POST {auth_cmd} -F "file=@{feature_for_upload}" "{url}"'
        cmd_for_log = f'curl -X POST {auth_log} -F "file=@{feature_for_upload}" "{url}"'
        self.xray_log.append(f"[CMD] {cmd_for_log}")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                self.xray_log.append(result.stdout)
            if result.stderr:
                self.xray_log.append(f"[ERROR] {result.stderr}")

            if result.returncode == 0:
                QMessageBox.information(self, "Success", "Test created/updated successfully in Jira/Xray.")
            else:
                QMessageBox.warning(
                    self, "Warning",
                    f"curl returned non-zero exit code ({result.returncode}). Check the log."
                )
        except Exception as e:
            self.xray_log.append(f"[EXCEPTION] {e}")
            QMessageBox.critical(self, "Error", f"Failed to run curl:\n{e}")
        finally:
            if tmp_to_cleanup and os.path.exists(tmp_to_cleanup):
                try: os.remove(tmp_to_cleanup)
                except Exception: pass

    def _run_jira_update_description(self):
        """
        Executa um curl para ATUALIZAR a descrição de um issue específico no Jira,
        usando a API padrão do Jira em vez do import do Xray.
        """
        self.save_login_config()
        auth_cmd, auth_log = self._build_auth_args()
        if not auth_cmd:
            return

        timestamp = self._render_last_update_line()

        new_description = f"A verificação da aplicação foi executada com sucesso.\nÚltima atualização: {timestamp}"
        json_data_raw = json.dumps({
            "fields": {
                "description": new_description
            }
        })

        # Escapar aspas duplas para uso no shell
        json_data_escaped = json_data_raw.replace('"', '\\"')


        base_url = "https://jerry.dieboldnixdorf.com/rest/api/2/issue"
        url = f"{base_url}/{JIRA_DUMMY_TEST_KEY}"

        # Comando curl para a API do Jira
        cmd = f'curl -D- -X PUT {auth_cmd} -H "Content-Type: application/json" -d "{json_data_escaped}" "{url}"'
        cmd_for_log = f'curl -D- -X PUT {auth_log} -H "Content-Type: application/json" -d "{json_data_escaped}" "{url}"'

        self.xray_log.append(f"\n[CMD] {cmd_for_log}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            
            output = result.stdout or ""
            error = result.stderr or ""
            
            if output:
                self.xray_log.append(f"[RESPONSE]\n{output}")
            if error:
                self.xray_log.append(f"[ERROR]\n{error}")

            # A API do Jira retorna 204 No Content em caso de sucesso na atualização
            if result.returncode == 0 and 'HTTP/1.1 204' in output:
                 QMessageBox.information(self, "Success", f"Connection test successful.\nIssue '{JIRA_DUMMY_TEST_KEY}' was updated in Jira.")
            else:
                QMessageBox.warning(self, "Warning", f"Could not update issue '{JIRA_DUMMY_TEST_KEY}'. Check the log for details.")

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
        """
        MODIFICADO: Não cria mais um teste com arquivo, apenas atualiza a descrição
        do teste definido em JIRA_DUMMY_TEST_KEY para verificar a conexão.
        """
        self.xray_log.clear()
        self.xray_log.append(f"--- Running Application Connection Test on issue: {JIRA_DUMMY_TEST_KEY} ---")
        self._run_jira_update_description()
