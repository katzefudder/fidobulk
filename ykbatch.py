import sys, requests, os, re
from urllib import request
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox, QPlainTextEdit, QPushButton, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from ykman import scripting as s
from ykman.otp import format_csv
from yubikit.yubiotp import YubiOtpSession, YubiOtpSlotConfiguration, SLOT

class YkBatch(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('YubiKey Demo')
        self.resize(300, 140)

        layout = QVBoxLayout()

        # set serial number
        serial_number = self.read_serial_number()
        label_text = f"FIDO Seriennummer: {serial_number}"
        self.label = QLabel(label_text, self)
        layout.addWidget(self.label)

        # try to set access token
        access_token_label_text = f"Access Token"
        self.access_token_label = QLabel(access_token_label_text, self)
        layout.addWidget(self.access_token_label)

        access_token = self.get_access_to_entra_id()
        access_token_text = f"{access_token}"
        self.access_token_text = QPlainTextEdit(access_token_text, self)
        self.access_token_text.setDocumentTitle('Access Token')
        self.access_token_text.setReadOnly(True)
        layout.addWidget(self.access_token_text)

        # fetch users and display a dropdown selection widget
        users = self.get_user_from_entra_id()
        self.user_combobox = QComboBox() # https://www.pythonguis.com/docs/qcombobox/
        for user in users:
            self.user_combobox.addItem(user['displayName'], user)
        layout.addWidget(self.user_combobox)
        self.user_combobox.currentIndexChanged.connect(self.on_user_selected)

        # submit data to API Button
        self.send_button = QPushButton("Absenden", self)
        self.send_button.clicked.connect(lambda: self.submit_form(serial_number))
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def submit_form(self, serial_number):
        """
        Sends a POST request to a local API with fixed JSON content.
        """

        selected_user = self.user_combobox.currentData()

        try:
            url = "http://localhost:5000/api"
            data = {
                "user": selected_user['displayName'],
                "serial_number": serial_number,
                "message": "lorem ipsum"
            }
            response = requests.post(url, json=data)
            response.raise_for_status()
            QMessageBox.information(self, "Erfolg", "✅ Nachricht erfolgreich gesendet!") # TODO: 

        except requests.RequestException as e:
            QMessageBox.critical(self, "Fehler", f"⛔️ Fehler beim Senden der Nachricht:\n{e}")

    def on_user_selected(self, index):
        selected_user = self.user_combobox.itemData
        return selected_user

    def read_serial_number(self):
        try:
            device = s.single()
            serial_number = device.info.serial

            if serial_number is None:
                raise ValueError("Serial number not available for this device.")

            return serial_number

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"⛔️ Fehler beim Abrufen der Seriennummer:\n{str(e)}")
            sys.exit(1)

    def get_user_from_entra_id(self):
        url = 'http://localhost:4711/graphql'
        query = """
        query {
            users {
                id
                displayName
                email
            }
        }
        """
        bearer_token = f"Bearer {self.get_access_to_entra_id()}"
        headers = {
            'Authorization': bearer_token,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            url,
            json={'query': query},
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return data['data']['users']

    # #######################
    def send_token_request(self, token_endpoint, headers, body):
        """
        Sends a token request to the specified token endpoint.

        Args:
            token_endpoint (str): The token endpoint URL.
            headers (dict): The HTTP headers for the request.
            body (dict): The request body.

        Returns:
            requests.Response: The response object.
        """
        NO_PROXY = {
            'no': 'pass',
        }
        response = requests.post(token_endpoint, data=body, headers=headers, verify=False, proxies=NO_PROXY)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response

    # Function setting the HTTP headers for Microsoft Graph API
    def set_http_headers(self, access_token):
        """
        Sets the HTTP headers required for making requests to the Microsoft Graph API.

        This function takes an access token as input and returns a dictionary containing
        the necessary headers for authenticating and formatting the requests to the Microsoft Graph API.

        Args:
            access_token (str): The access token obtained from the authentication process.

        Returns:
            dict: A dictionary containing the HTTP headers for the Microsoft Graph API requests.
        """
        return {
            "Accept": "application/json",
            "Authorization": access_token,
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
        }


    # Function to construct request body when accessing Microsoft Graph API
    def construct_request_body(self, client_id, client_secret):
        """
        Constructs the request body for obtaining an access token.

        Args:
            client_id (str): The client ID of the application.
            client_secret (str): The client secret of the application.

        Returns:
            dict: The constructed request body.
        """
        return {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }


    # Function to parse access token in response from Microsoft Graph API
    def extract_access_token(self, response):
        """
        Extracts the access token from the response.

        Args:
            response (requests.Response): The response object.

        Returns:
            str: The extracted access token.
        """
        access_token = re.search('"access_token":"([^"]+)"', str(response.content))
        if not access_token:
            raise ValueError("Access token not found in response")
        return access_token.group(1)


    # Function to retrieve acces token from Microsoft Graph API
    def get_access_token_for_microsoft_graph(self, client_id, client_secret, tenant_id):
        """
        Retrieves an access token for accessing Microsoft Graph API using OAuth client credentials flow.

        Args:
            client_id (str): The client ID of the application.
            client_secret (str): The client secret of the application.
            tenant_id (str): The name of the Entra directory as an fqdn.

        Returns:
            str: The access token.
        """

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        #token_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_endpoint = f"http://localhost:4000/auth/token"

        body = self.construct_request_body(client_id, client_secret)

        token_response = self.send_token_request(token_endpoint, headers, body)

        access_token = self.extract_access_token(token_response)

        return access_token


    def get_access_to_entra_id(self):
        # Config attributes we need
        client_id = "clientId"
        client_secret = "secret"
        tenant_id = "domainName.onmicrosoft.com"

        access_token = self.get_access_token_for_microsoft_graph(client_id, client_secret, tenant_id)
        return access_token


if __name__ == '__main__':
    

    app = QApplication(sys.argv)
    window = YkBatch()
    access_token = window.get_access_to_entra_id()
    window.show()
    sys.exit(app.exec_())
