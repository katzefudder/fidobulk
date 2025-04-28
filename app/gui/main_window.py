from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPlainTextEdit, QPushButton, QComboBox, QMessageBox, QLineEdit, QDialog
from lib.device import Device
from lib.auth import get_access_token
from lib.users import fetch_users
from lib.api_client import submit_user_data

class YkBatch(QWidget):

    device = []
    random_pin = "00000"

    def __init__(self):
        super().__init__()
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle("YubiKey Demo")
        self.resize(300, 140)
        device_instance = Device()
        self.device = device_instance
        layout = QVBoxLayout()

        try:
            self.serial_number = self.device.get_serial_number()
            self.label = QLabel(f"FIDO Seriennummer: {self.serial_number}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"⛔️ Seriennummer:\n{e}")
            self.serial_number = "Unbekannt"
            self.label = QLabel("FIDO Seriennummer: Fehler")
        layout.addWidget(self.label)

        self.access_token = get_access_token("clientId", "secret", "domainName.onmicrosoft.com")

        if device_instance.pin_already_set:
            self.pin_text_label = QLabel("Pin schon gesetzt. Um diesen neu zu setzen, bitte FIDO-Stick zurücksetzen.")
            layout.addWidget(self.pin_text_label)
        else:
            self.users = fetch_users(self.access_token)
            self.user_combobox = QComboBox()
            for user in self.users:
                self.user_combobox.addItem(user['displayName'], user)
            layout.addWidget(self.user_combobox)
            self.set_random_pin = QPushButton("Neue zufällige PIN setzen")
            self.set_random_pin.clicked.connect(self.handle_set_random_pin)
            layout.addWidget(self.set_random_pin)

            # self.send_button = QPushButton("Absenden")
            # self.send_button.clicked.connect(self.handle_submit)
            # layout.addWidget(self.send_button)

        # self.reset_button = QPushButton("Reset Fido Stick")
        # self.reset_button.clicked.connect(self.handle_reset)
        # layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def handle_submit(self):
        selected_user = self.user_combobox.currentData()
        # TODO: update GUI after successfully setting the pin
        try:
            submit_user_data(selected_user, self.random_pin, self.serial_number)
            QMessageBox.information(self, "Erfolg", f"✅ Pin für {selected_user.displayName} gesetzt und zur Datenbank übermittelt!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"⛔️ Fehler:\n{e}")

    def handle_set_random_pin(self):
        pin_value = self.device.generate_pin()
        print(f"pin set: {pin_value}")
        # TODO: update GUI after successfully setting the pin
        try:
            self.random_pin = pin_value
            self.device.set_pin(pin_value)
            QMessageBox.information(self, "Erfolg", "✅ PIN erfolgreich gesetzt: " + str(pin_value))
            self.set_random_pin.hide()
            
            try:
                selected_user = self.user_combobox.currentData()
                submit_user_data(selected_user, self.random_pin, self.serial_number)
                QMessageBox.information(self, "Erfolg", f"✅ Pin für {selected_user} gesetzt und zur Datenbank übermittelt!")
                self.user_combobox.hide()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"⛔️ Fehler:\n{e}")

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"⛔️ Fehler:\n{e}")

    # def handle_reset(self):
    #     reply = QMessageBox.question(
    #         self, 'Reset bestätigen', 
    #         "Der Fido Stick wird zurückgesetzt: sicher?",
    #         QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    #     )
    #     if reply == QMessageBox.Yes:
    #         # Perform reset actions
    #         QMessageBox.critical(self, "Info", f"Bitte den Fidokey berühren, halten und OK klicken")
    #         self.device.reset()
    #         QMessageBox.information(self, "Reset", "Der Fido Stick wurde zurückgesetzt.")

        
