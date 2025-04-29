from ykman import scripting as s
from fido2.hid import CtapHidDevice
from fido2.ctap2 import Ctap2
from fido2.ctap2.pin import ClientPin
from fido2.ctap import CtapError
import secrets
import string
import time
import threading
import logging

class Device:
    
    def __init__(self):
        super().__init__()
        self.logger = self._setup_logger()        

        self.device = None
        self.pin_already_set = False
        self._stop_event = threading.Event()
        self._wait_for_device()
        self.pin_already_set = self._is_pin_already_set()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)  # You can choose DEBUG, INFO, WARNING, etc.

        # Set up console output
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _find_device(self):
        device = next(CtapHidDevice.list_devices(), None)
        if not device:
            raise RuntimeError("No FIDO2 device found.")
        return device

    def _wait_for_device(self):
        """Background thread function: keep checking until a device appears."""
        while not self._stop_event.is_set():
            try:
                self.device = self._find_device()
                self.logger.info("FIDO Stick gefunden!")
                break
            except RuntimeError:
                self.logger.info("Kein FIDO Stick gefunden. Suche...")
                time.sleep(1)  # Wait 1 second before retrying

    def start_waiting_for_device(self):
        """Start the background thread."""
        thread = threading.Thread(target=self._wait_for_device, daemon=True)
        thread.start()

    def stop_waiting_for_device(self):
        """Stop the waiting loop."""
        self._stop_event.set()

    def get_device(self):
        return self.device

    def is_device_connected(self):
        return self.device is not None

    def get_serial_number(self):
        """
        A specialty to Yubikeys: using ykman to retrieve the key's serial number
        """
        device = s.single()
        serial = device.info.serial
        if serial is None:
            raise ValueError("Serial number not available.")
        return serial

    # def _reset_device(self, event):
    #     try:
    #         ctap2 = Ctap2(self.device)
    #         ctap2.reset()  # This call blocks until reset is complete
    #         dev = self.wait_for_device()
    #         print(f"dev: {dev}")
    #         print("✅ Device has been reset successfully.")
    #         event.set()
    #     except CtapError as e:
    #         if e.code == CtapError.ERR.NOT_ALLOWED:
    #             self.logger.error(f"error: {e}")
    #         else:
    #             self.logger.error(f"❌ Reset failed: {e}")

    def _is_pin_already_set(self):
        ctap2 = Ctap2(self.device)
        return ctap2.info.options.get("clientPin")

    def set_pin(self, new_pin):
        ctap2 = Ctap2(self.device)
        if ctap2.info.options.get("clientPin"):
            raise RuntimeError("PIN is already set for this device.")
        client_pin = ClientPin(ctap2)

        try:
            client_pin.set_pin(new_pin)
        except CtapError as e:
            self.logger.error(f"❌ Fehler beim Setzen der PIN: {e}")
        
        return

    def generate_pin(self):
        disallowed_pins = [
            "123456",
            "123123",
            "654321",
            "123321",
            "112233",
            "121212",
            "520520",
            "123654",
            "159753",
        ]

        while True:
            digits = "".join(secrets.choice(string.digits) for _ in range(6))
            # Check if PIN is not trivial and not in banned list
            if len(set(digits)) != 1 and digits not in disallowed_pins:
                return digits