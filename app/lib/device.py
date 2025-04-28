from ykman import scripting as s
from fido2.hid import CtapHidDevice
from fido2.ctap2 import Ctap2
from fido2.ctap2.pin import ClientPin
from fido2.ctap import CtapError
import secrets
import string
import threading
import pyscard

class Device:
    device = {}
    pin_already_set = False

    def __init__(self):
        self.device = self._find_device()
        self.pin_already_set = self.pin_already_set()
        print("Pin already set: " + str(self.pin_already_set))


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
        """
        A specialty to Yubikeys: using ykman to retrieve the key's serial number
        """
        device = s.single()
        serial = device.info.serial
        if serial is None:
            raise ValueError("Serial number not available.")
        return serial

    def _reset_device(self, event):
        try:
            ctap2 = Ctap2(self.device)
            ctap2.reset()  # This call blocks until reset is complete
            dev = self.wait_for_device()
            print(f"dev: {dev}")
            print("✅ Device has been reset successfully.")
            event.set()
        except CtapError as e:
            if e.code == CtapError.ERR.NOT_ALLOWED:
                print(f"error: {e}")
            else:
                print(f"❌ Reset failed: {e}")

    def wait_for_device(self, timeout=10):
        """Wait for a FIDO device to be available again."""
        start = time.time()
        while time.time() - start < timeout:
            devices = list(CtapHidDevice.list_devices())
            if devices:
                return devices[0]
            time.sleep(0.2)
        raise TimeoutError("Timeout waiting for FIDO device to reappear.")

    def reset(self):
        reset_success = threading.Event()
        reset_thread = threading.Thread(target=self._reset_device, args=(reset_success,))
        reset_thread.start()

    def pin_already_set(self):
        ctap2 = Ctap2(self.device)
        return ctap2.info.options.get("clientPin")

    def set_pin(self, new_pin):
        ctap2 = Ctap2(self.device)
        if ctap2.info.options.get("clientPin"):
            print("\tPIN already set for the device")   # TODO: should display a hint in GUI just in case PIN has already been set
            quit()
        client_pin = ClientPin(ctap2)

        try:
            client_pin.set_pin(new_pin)
        except CtapError as e:
            print(f"❌ Fehler beim Setzen der PIN: {e}")
        
        return

    def set_pin_minimum_length(self):
        ctap = Ctap2(self.device)
        if ctap.info.options.get("setMinPINLength"):
            client_pin = ClientPin(ctap)
            token = client_pin.get_pin_token(
                pin, ClientPin.PERMISSION.AUTHENTICATOR_CFG
            )
            config = Config(ctap, client_pin.protocol, token)
            print("\tGoing to set the minimum pin length to 6.")
            config.set_min_pin_length(min_pin_length=6)
            print("\tGoing to force a PIN change on first use.")
            config.set_min_pin_length(force_change_pin=True)

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