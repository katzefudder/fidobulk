from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPlainTextEdit, QPushButton, QComboBox, QMessageBox
from lib.device import get_serial_number
from lib.auth import get_access_token
from lib.users import fetch_users
from lib.api_client import submit_user_data

class YkBatch(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YubiKey Demo")
        self.resize(300, 140)
        layout = QVBoxLayout()

        try:
            self.serial_number = get_serial_number()
            self.label = QLabel(f"FIDO Seriennummer: {self.serial_number}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"⛔️ Seriennummer:\n{e}")
            self.serial_number = "Unbekannt"
            self.label = QLabel("FIDO Seriennummer: Fehler")
        layout.addWidget(self.label)

        self.access_token = get_access_token("clientId", "secret", "domainName.onmicrosoft.com")
        self.access_token_text = QPlainTextEdit(self.access_token)
        self.access_token_text.setReadOnly(True)
        layout.addWidget(self.access_token_text)

        self.users = fetch_users(self.access_token)
        self.user_combobox = QComboBox()
        for user in self.users:
            self.user_combobox.addItem(user['displayName'], user)
        layout.addWidget(self.user_combobox)

        self.send_button = QPushButton("Absenden")
        self.send_button.clicked.connect(self.handle_submit)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def handle_submit(self):
        selected_user = self.user_combobox.currentData()
        try:
            submit_user_data(selected_user, self.serial_number)
            QMessageBox.information(self, "Erfolg", "✅ Nachricht gesendet!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"⛔️ Fehler:\n{e}")
