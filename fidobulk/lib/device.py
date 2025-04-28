import time
import threading
import secrets
import string
import logging

from ykman import scripting as s
from fido2.hid import CtapHidDevice
from fido2.ctap2 import Ctap2
from fido2.ctap2.pin import ClientPin
from fido2.ctap import CtapError

logger = logging.getLogger(__name__)

class Device:
    def __init__(self):
        self.device = self._find_device()
        self.pin_set = self._is_pin_already_set()
        logger.info("PIN already set: %s", self.pin_set)

    def _find_device(self):
        device = next(CtapHidDevice.list_devices(), None)
        if not device:
            raise RuntimeError("No FIDO2 device found.")
        return device

    def get_device(self):
        return self.device

    def is_device_connected(self):
        return self.device is not None

    def get_serial_number(self):
        """Retrieve the serial number (YubiKey-specific)."""
        device = s.single()
        serial = device.info.serial
        if serial is None:
            raise ValueError("Serial number not available.")
        return serial

    def _reset_device(self, event):
        try:
            ctap2 = Ctap2(self.device)
            ctap2.reset()
            self.device = self._wait_for_device()
            logger.info("✅ Device reset successfully.")
            event.set()
        except CtapError as e:
            if e.code == CtapError.ERR.NOT_ALLOWED:
                logger.warning("Reset not allowed: %s", e)
            else:
                logger.error("❌ Reset failed: %s", e)

    def _wait_for_device(self, timeout=10):
        """Wait for a FIDO2 device to become available."""
        start = time.time()
        while time.time() - start < timeout:
            devices = list(CtapHidDevice.list_devices())
            if devices:
                return devices[0]
            time.sleep(0.2)
        raise TimeoutError("Timeout waiting for FIDO2 device to reappear.")

    def reset(self):
        """Initiate device reset in a separate thread."""
        reset_success = threading.Event()
        reset_thread = threading.Thread(target=self._reset_device, args=(reset_success,))
        reset_thread.daemon = True
        reset_thread.start()
        return reset_thread, reset_success

    def _is_pin_already_set(self):
        ctap2 = Ctap2(self.device)
        return ctap2.info.options.get("clientPin", False)

    def set_pin(self, new_pin):
        """Set a new PIN for the device."""
        if self.pin_set:
            raise RuntimeError("PIN is already set for this device.")

        ctap2 = Ctap2(self.device)
        client_pin = ClientPin(ctap2)

        try:
            client_pin.set_pin(new_pin)
            logger.info("✅ PIN set successfully.")
        except CtapError as e:
            logger.error("❌ Error setting PIN: %s", e)
            raise

    def set_minimum_pin_length(self, pin):
        """Configure the minimum PIN length if supported."""
        ctap = Ctap2(self.device)
        if ctap.info.options.get("setMinPINLength"):
            client_pin = ClientPin(ctap)
            token = client_pin.get_pin_token(pin, ClientPin.PERMISSION.AUTHENTICATOR_CFG)

            from fido2.ctap2.config import Config
            config = Config(ctap, client_pin.protocol, token)

            logger.info("Setting minimum PIN length to 6...")
            config.set_min_pin_length(min_pin_length=6)

            logger.info("Forcing PIN change on first use...")
            config.set_force_pin_change(force_change=True)
        else:
            logger.warning("Device does not support setting minimum PIN length.")

    def generate_pin(self):
        """Generate a random, non-trivial 6-digit PIN."""
        disallowed_pins = {
            "123456", "123123", "654321", "123321",
            "112233", "121212", "520520", "123654", "159753",
        }

        while True:
            digits = ''.join(secrets.choice(string.digits) for _ in range(6))
            if len(set(digits)) > 1 and digits not in disallowed_pins:
                return digits
