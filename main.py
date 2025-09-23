import sys
import os
import subprocess
import resources_rc
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QTextEdit, QMessageBox,
    QSplitter, QLabel, QToolButton, QFrame, QLineEdit, QTabWidget,
    QRadioButton, QButtonGroup, QGroupBox, QStackedWidget, QFileIconProvider
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from core.parser import parse_robot_file

LOGIN_CONFIG_PATH = "login_config.json"

class FeatureCreatorPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Header (linha superior) ---
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        # Botão para selecionar pasta (à esquerda)
        self.folder_button = QPushButton("Selecionar Pasta")
        self.folder_button.clicked.connect(self.parent.select_folder)
        header.addWidget(self.folder_button)

        # "Checkbox" de subpastas → botão toggle (destacado quando ligado)
        self.subfolders_checkbox = QPushButton("Incluir subpastas")
        self.subfolders_checkbox.setObjectName("btnSubfolders")
        self.subfolders_checkbox.setCheckable(True)
        self.subfolders_checkbox.setChecked(self.parent.include_subfolders)
        self.subfolders_checkbox.setToolTip("Alternar inclusão de subpastas")
        self.subfolders_checkbox.toggled.connect(
            lambda checked: self.parent.toggle_subfolders(Qt.Checked if checked else Qt.Unchecked)
        )
        header.addWidget(self.subfolders_checkbox)

        # --- Novos campos no header ---
        self.parent.project_input = QLineEdit()
        self.parent.project_input.setPlaceholderText("Projeto (@KEYDOTESTE)")
        self.parent.project_input.setText("@PROJECTKEY")  # valor padrão
        self.parent.project_input.textChanged.connect(self.parent._on_project_changed)
        header.addWidget(self.parent.project_input)

        self.parent.tags_input = QLineEdit()
        self.parent.tags_input.setPlaceholderText("Tags (@tag1 @tag2)")
        self.parent.tags_input.textChanged.connect(self.parent._on_tags_changed)
        header.addWidget(self.parent.tags_input)

        header.addStretch()
        # O botão de tema será adicionado pelo MainWindow

        layout.addLayout(header)

        # --- Conteúdo principal: Splitter (esquerda: arquivos+log, direita: preview) ---
        self.parent.splitter = QSplitter(Qt.Horizontal)
        self.parent.splitter.setObjectName("mainSplitter")
        self.parent.splitter.setHandleWidth(8)

        # Lado esquerdo: arquivos + log empilhados
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self.parent.file_list = QListWidget()
        self.parent.file_list.itemClicked.connect(self.parent.show_preview)
        self.parent.file_list.setSelectionMode(QListWidget.SingleSelection)
        left_layout.addWidget(self.parent.file_list, 1)  # metade superior

        self.parent.log_output = QTextEdit()
        self.parent.log_output.setReadOnly(True)
        self.parent.log_output.setPlaceholderText("Logs do sistema aparecerão aqui...")
        left_layout.addWidget(self.parent.log_output, 1)  # metade inferior

        self.parent.splitter.addWidget(left_widget)

        # --- Botão para voltar à visualização geral ---
        self.parent.back_button = QPushButton("Visualização Geral")
        self.parent.back_button.setToolTip("Voltar para a visualização do arquivo .feature final")
        self.parent.back_button.clicked.connect(self.parent.show_overall_preview)
        self.parent.back_button.setVisible(False)
        # Adicione o botão acima do preview (lado direito)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        right_layout.addWidget(self.parent.back_button, 0)

        self.parent.preview = QTextEdit()
        self.parent.preview.setReadOnly(True)
        right_layout.addWidget(self.parent.preview, 1)

        self.parent.splitter.addWidget(right_widget)

        self.parent.splitter.setSizes([350, 550])  # Ajuste conforme preferir
        layout.addWidget(self.parent.splitter, 3)

        # --- Rodapé fixo (sumário + Gerar .feature) ---
        self.parent.footer = QFrame()
        self.parent.footer.setObjectName("footerBar")
        footer_layout = QHBoxLayout(self.parent.footer)
        footer_layout.setContentsMargins(12, 6, 12, 6)
        footer_layout.setSpacing(8)

        self.parent.lblSummary = QLabel()
        self.parent.lblSummary.setObjectName("lblSummary")
        footer_layout.addWidget(self.parent.lblSummary)

        footer_layout.addStretch()

        self.parent.generate_button = QPushButton("Gerar .feature")
        self.parent.generate_button.clicked.connect(self.parent.generate_feature)
        footer_layout.addWidget(self.parent.generate_button)

        # --- Botão de Reset ---
        self.parent.reset_button = QPushButton("Resetar")
        self.parent.reset_button.setToolTip("Limpa tudo e volta ao estado inicial")
        self.parent.reset_button.clicked.connect(self.parent.reset_all)
        footer_layout.addWidget(self.parent.reset_button)

        layout.addWidget(self.parent.footer, 0)
        self.setLayout(layout)

class XrayTestPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.load_login_config()  # Carrega ao iniciar

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # --- Login Group ---
        login_group = QGroupBox("Login no Jira/Xray")
        login_layout = QVBoxLayout(login_group)

        self.radio_userpass = QRadioButton("Usuário e Senha")
        self.radio_token = QRadioButton("Token do Jira")
        self.radio_userpass.setChecked(True)
        login_layout.addWidget(self.radio_userpass)
        login_layout.addWidget(self.radio_token)

        self.login_method_group = QButtonGroup()
        self.login_method_group.addButton(self.radio_userpass)
        self.login_method_group.addButton(self.radio_token)

        # Campos de usuário/senha/token em um QStackedWidget
        self.login_stack = QStackedWidget()

        # Página 0: Usuário e Senha
        userpass_widget = QWidget()
        userpass_layout = QVBoxLayout(userpass_widget)
        self.user_field = QLineEdit()
        self.user_field.setPlaceholderText("Usuário Jira")
        self.pass_field = QLineEdit()
        self.pass_field.setPlaceholderText("Senha Jira")
        self.pass_field.setEchoMode(QLineEdit.Password)
        userpass_layout.addWidget(self.user_field)
        userpass_layout.addWidget(self.pass_field)
        self.login_stack.addWidget(userpass_widget)

        # Página 1: Token
        token_widget = QWidget()
        token_layout = QVBoxLayout(token_widget)
        self.token_field = QLineEdit()
        self.token_field.setPlaceholderText("Token Jira")
        token_layout.addWidget(self.token_field)
        self.login_stack.addWidget(token_widget)

        login_layout.addWidget(self.login_stack)

        # Alterna páginas do stack conforme seleção
        self.radio_userpass.toggled.connect(
            lambda checked: self.login_stack.setCurrentIndex(0 if checked else 1)
        )
        self.radio_token.toggled.connect(
            lambda checked: self.login_stack.setCurrentIndex(1 if checked else 0)
        )
        self.login_stack.setCurrentIndex(0)

        layout.addWidget(login_group)

        # --- Seleção de arquivo .feature ---
        file_group = QGroupBox("Arquivo .feature para criar teste")
        file_layout = QHBoxLayout(file_group)
        self.feature_file_path = QLineEdit()
        self.feature_file_path.setPlaceholderText("Selecione um arquivo .feature")
        self.feature_file_path.setReadOnly(True)
        file_layout.addWidget(self.feature_file_path)
        self.select_file_btn = QPushButton("Selecionar Arquivo")
        self.select_file_btn.clicked.connect(self.select_feature_file)
        file_layout.addWidget(self.select_file_btn)
        layout.addWidget(file_group)

        # --- Botão de criar teste ---
        self.create_test_btn = QPushButton("Criar Teste no Xray")
        self.create_test_btn.clicked.connect(self.create_xray_test)
        layout.addWidget(self.create_test_btn)

        # --- Log de saída ---
        self.xray_log = QTextEdit()
        self.xray_log.setReadOnly(True)
        self.xray_log.setPlaceholderText("Saída do comando aparecerá aqui...")
        layout.addWidget(self.xray_log, 1)

        self.setLayout(layout)

    def select_feature_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo .feature", "", "Feature Files (*.feature)")
        if file_path:
            self.feature_file_path.setText(file_path)

    def save_login_config(self):
        config = {
            "login_type": "userpass" if self.radio_userpass.isChecked() else "token",
            "user": self.user_field.text() if self.radio_userpass.isChecked() else "",
            "token": self.token_field.text() if self.radio_token.isChecked() else ""
        }
        try:
            with open(LOGIN_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except Exception as e:
            # Opcional: logar erro
            pass

    def load_login_config(self):
        try:
            with open(LOGIN_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            if config.get("login_type") == "userpass":
                self.radio_userpass.setChecked(True)
                self.user_field.setText(config.get("user", ""))
                self.token_field.setText("")
            else:
                self.radio_token.setChecked(True)
                self.token_field.setText(config.get("token", ""))
                self.user_field.setText("")
        except Exception:
            pass  # Se não existir, ignora

    def create_xray_test(self):
        # Salva o login/tipo antes de executar
        self.save_login_config()

        # Validação
        if not self.feature_file_path.text():
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo .feature para criar o teste.")
            return

        if self.radio_userpass.isChecked():
            user = self.user_field.text().strip()
            passwd = self.pass_field.text().strip()
            if not user or not passwd:
                QMessageBox.warning(self, "Aviso", "Preencha usuário e senha do Jira.")
                return
            auth = f"-u {user}:{passwd}"
        else:
            token = self.token_field.text().strip()
            if not token:
                QMessageBox.warning(self, "Aviso", "Preencha o token do Jira.")
                return
            auth = f"-H \"Authorization: Bearer {token}\""

        # Comando curl de exemplo (ajuste conforme sua API do Xray)
        feature_file = self.feature_file_path.text()
        url = "https://seu-jira/rest/raven/2.0/import/feature"
        if self.radio_userpass.isChecked():
            cmd = f'curl -X POST {auth} -F "file=@{feature_file}" "{url}"'
        else:
            cmd = f'curl -X POST {auth} -F "file=@{feature_file}" "{url}"'

        self.xray_log.append(f"[CMD] {cmd}")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            self.xray_log.append(result.stdout)
            if result.stderr:
                self.xray_log.append(f"[ERRO] {result.stderr}")
        except Exception as e:
            self.xray_log.append(f"[EXCEPTION] {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot → Cucumber → Jira")
        self.resize(900, 600)

        # ---------- Estado inicial ----------
        self.dark_mode = True
        self.include_subfolders = False
        self.folder = None
        self.all_features = []

        # Contadores
        self.folder_count = 0
        self.file_count = 0
        self.feature_count = 0
        self.scenario_count = 0

        # Chave do projeto e tags para Jira
        self.project_key = ""
        self.tags = ""

        # --- Abas ---
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        # Páginas
        self.feature_creator_page = FeatureCreatorPage(self)
        self.xray_test_page = XrayTestPage(self)

        self.tabs.addTab(self.feature_creator_page, "Criar .feature")
        self.tabs.addTab(self.xray_test_page, "Criar Teste no Xray")

        # --- Botão de tema no topo direito das abas ---
        self.theme_button = QToolButton(self)
        self.theme_button.setObjectName("btnTheme")
        self.theme_button.setToolTip("Alternar tema")
        self.theme_button.setAutoRaise(True)
        self.theme_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.theme_button.setIconSize(QSize(20, 20))
        self.theme_button.setIcon(QIcon(":/icons/sun.svg") if self.dark_mode else QIcon(":/icons/moon.svg"))
        self.theme_button.setText("")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.tabs.setCornerWidget(self.theme_button, Qt.TopRightCorner)

        # Layout principal da janela
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Tema + sumário inicial
        self.apply_theme()
        self._update_summary()

    # --------- Funções herdadas da página de criação de feature ---------
    def _update_summary(self):
        if hasattr(self, "lblSummary"):
            self.lblSummary.setText(
                f"Pastas: {self.folder_count} • Arquivos: {self.file_count} • "
                f"Features: {self.feature_count} • Cenários: {self.scenario_count}"
            )

    def toggle_subfolders(self, state: int):
        self.include_subfolders = (state == Qt.Checked)
        if hasattr(self, "log_output"):
            self.log_output.append(f"[INFO] Incluir subpastas: {self.include_subfolders}")

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
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta com arquivos .robot")
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

            self.log_output.append(f"[INFO] Pasta selecionada: {folder}")

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
                preview_text = "Nenhum bloco de Feature encontrado nos arquivos."
            self.preview.setPlainText(preview_text)

            self.log_output.append("\n[RESUMO FINAL]")
            self.log_output.append(f"- Total de pastas analisadas: {self.folder_count}")
            self.log_output.append(f"- Total de arquivos .robot: {self.file_count}")
            self.log_output.append(f"- Total de Features extraídas: {self.feature_count}")
            self.log_output.append(f"- Total de Cenários extraídos: {self.scenario_count}\n")

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
                    f"{stats['features']} Feature(s), {stats['scenarios']} Cenário(s)"
                )
            else:
                self.log_output.append(f"[WARN] Nenhum Feature encontrado em {full_path}")

        except Exception as e:
            self.log_output.append(f"[ERRO] Falha ao parsear {full_path}: {e}")

    def show_preview(self, item):
        file_path = item.text()
        try:
            features, _ = parse_robot_file(file_path)
            if features:
                preview_text = "\n\n---\n\n".join(self._apply_project_and_tags(features))
            else:
                preview_text = "Nenhum bloco de Feature encontrado neste arquivo."
        except Exception as e:
            preview_text = f"[ERRO] Falha ao parsear {file_path}: {e}"
        self.preview.setPlainText(preview_text)
        self.back_button.setVisible(True)

    def show_overall_preview(self):
        self.file_list.clearSelection()
        if self.all_features:
            preview_text = "\n\n---\n\n".join(self._apply_project_and_tags(self.all_features))
        else:
            preview_text = "Nenhum bloco de Feature encontrado nos arquivos."
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
        self.log_output.append("[INFO] Aplicação resetada.")

    def generate_feature(self):
        if not self.all_features:
            QMessageBox.warning(self, "Aviso", "Nenhum conteúdo para gerar .feature!")
            return

        if not self.project_key or not self.tags:
            msg = "Você tem certeza que quer gerar o arquivo sem adicionar "
            if not self.project_key and not self.tags:
                msg += "projeto e tags?"
            elif not self.project_key:
                msg += "projeto?"
            else:
                msg += "tags?"
            reply = QMessageBox.question(
                self, "Atenção", msg,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                self.log_output.append("[INFO] Geração de arquivo cancelada pelo usuário.")
                return

        output_path = os.path.join(self.folder, "combined.feature")
        try:
            features_with_project_and_tags = self._apply_project_and_tags(self.all_features)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(features_with_project_and_tags))

            QMessageBox.information(self, "Sucesso", f"Arquivo salvo em:\n{output_path}")
            self.log_output.append(f"[OK] Arquivo .feature gerado em {output_path}")

            # Abre no explorador
            if sys.platform == "win32":
                subprocess.Popen(f'explorer /select,"{output_path}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", output_path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(output_path)])

            # --- Integração com a página Xray ---
            reply = QMessageBox.question(
                self,
                "Criar Teste no Xray",
                "Deseja criar os testes no Jira Xray usando este arquivo agora?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                # Troca para a aba Xray
                self.tabs.setCurrentWidget(self.xray_test_page)
                # Preenche o campo do arquivo .feature na página Xray
                self.xray_test_page.feature_file_path.setText(output_path)
                # Carrega login salvo
                self.xray_test_page.load_login_config()
                # Checa se já há login/token salvo
                login_type = None
                user_ok = False
                token_ok = False
                try:
                    with open(LOGIN_CONFIG_PATH, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    login_type = config.get("login_type")
                    if login_type == "userpass":
                        user_ok = bool(config.get("user"))
                    elif login_type == "token":
                        token_ok = bool(config.get("token"))
                except Exception:
                    pass

                if (login_type == "userpass" and user_ok) or (login_type == "token" and token_ok):
                    # Executa automaticamente a criação do teste
                    self.xray_test_page.create_xray_test()
                # Senão, só deixa o arquivo preenchido e espera o usuário

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar arquivo: {e}")
            self.log_output.append(f"[ERRO] Falha ao salvar arquivo: {e}")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self._update_theme_icon()

    def _update_theme_icon(self):
        if isinstance(self.theme_button, QToolButton):
            self.theme_button.setIcon(QIcon(":/icons/sun.svg") if self.dark_mode else QIcon(":/icons/moon.svg"))
            self.theme_button.setText("")

    def apply_theme(self):
        app = QApplication.instance()
        app.setStyleSheet("")  # Limpa o estilo anterior

        if self.dark_mode:
            style = """
                QMainWindow, QWidget { background-color: #121212; color: #ffffff; }
                QLabel { color: #ffffff; }

                QPushButton {
                    background-color: #333333;
                    color: #ffffff;
                    border-radius: 6px;
                    padding: 6px 10px;
                    border: 1px solid #4a4a4a;
                }
                QPushButton:hover { background-color: #444444; }

                QListWidget, QTextEdit, QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #2a2a2a;
                }

                QPushButton#btnSubfolders {
                    background: #2c2c2c;
                    border: 1px solid #4a4a4a;
                    color: #ffffff;
                }
                QPushButton#btnSubfolders:hover { background: #3a3a3a; }
                QPushButton#btnSubfolders:checked {
                    background: #2d7d46;
                    color: #ffffff;
                    border-color: #2d7d46;
                }
                QPushButton#btnSubfolders:checked:hover { background: #2f8b4f; }

                QToolButton#btnTheme {
                    border: none;
                    padding: 4px;
                    margin: 2px;
                    border-radius: 6px;
                }
                QToolButton#btnTheme:hover { background: rgba(255,255,255,0.08); }

                QFrame#footerBar {
                    background-color: #121212;
                    border-top: 1px solid #2a2a2a;
                }
                QLabel#lblSummary { color: #aaaaaa; }

                QSplitter#mainSplitter::handle {
                    background-color: #1b1b1b;
                    border: none;
                    margin: 0;
                }
                QSplitter#mainSplitter::handle:horizontal {
                    width: 8px;
                    border-left: 1px solid rgba(255,255,255,0.06);
                    background-clip: padding;
                }
                QSplitter#mainSplitter::handle:horizontal:hover {
                    background-color: #252525;
                    border-left-color: rgba(255,255,255,0.14);
                }
                QSplitter#mainSplitter::handle:horizontal:pressed {
                    background-color: #2a2a2a;
                    border-left-color: rgba(255,255,255,0.18);
                }
            """
        else:
            style = """
                QMainWindow, QWidget { background-color: #f7f7f7; color: #222222; }
                QLabel { color: #222222; }

                QPushButton {
                    background-color: #ffffff;
                    color: #222222;
                    border-radius: 6px;
                    padding: 6px 10px;
                    border: 1px solid #bdbdbd;
                }
                QPushButton:hover { background-color: #f0f0f0; }

                QListWidget, QTextEdit, QLineEdit {
                    background-color: #ffffff;
                    color: #222222;
                    border: 1px solid #dcdcdc;
                }

                QPushButton#btnSubfolders {
                    background: #f6f6f6;
                    border: 1px solid #bdbdbd;
                    color: #333333;
                }
                QPushButton#btnSubfolders:hover { background: #eeeeee; }
                QPushButton#btnSubfolders:checked {
                    background: #2d7d46;
                    color: #ffffff;
                    border-color: #2d7d46;
                }
                QPushButton#btnSubfolders:checked:hover { background: #2f8b4f; }

                QToolButton#btnTheme {
                    border: none;
                    padding: 4px;
                    margin: 2px;
                    border-radius: 6px;
                }
                QToolButton#btnTheme:hover { background: rgba(0,0,0,0.08); }

                QFrame#footerBar {
                    background-color: #f7f7f7;
                    border-top: 1px solid #dcdcdc;
                }
                QLabel#lblSummary { color: #555555; }

                QSplitter#mainSplitter::handle {
                    background-color: rgba(0,0,0,0.04);
                    border: none;
                    margin: 0;
                }
                QSplitter#mainSplitter::handle:horizontal {
                    width: 8px;
                    border-left: 1px solid #dcdcdc;
                    background-clip: padding;
                }
                QSplitter#mainSplitter::handle:horizontal:hover {
                    background-color: rgba(0,0,0,0.08);
                    border-left-color: #c8c8c8;
                }
                QSplitter#mainSplitter::handle:horizontal:pressed {
                    background-color: rgba(0,0,0,0.10);
                    border-left-color: #bdbdbd;
                }
            """

        app.setStyleSheet(style)
        self._update_theme_icon()
        if hasattr(self, "splitter"):
            self.splitter.update()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
