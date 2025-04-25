from ykman import scripting as s
from fido2.hid import CtapHidDevice
from fido2.ctap2 import Ctap2
from fido2.ctap2.pin import ClientPin
from fido2.ctap import CtapError
import threading

class Device:
    def __init__(self):
        self.device = self._find_device()

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
            print("✅ Device has been reset successfully.")
            event.set()
        except CtapError as e:
            if e.code == CtapError.ERR.NOT_ALLOWED:
                print(f"error: {e}")
            else:
                print(f"❌ Reset failed: {e}")

    def reset(self):
        reset_success = threading.Event()
        reset_thread = threading.Thread(target=self._reset_device, args=(reset_success,))
        reset_thread.start()

    def set_pin(self, new_pin):
        ctap2 = Ctap2(self.device)
        client_pin = ClientPin(ctap2)

        try:
            client_pin.set_pin(new_pin)
        except CtapError as e:
            print(f"❌ Fehler beim Setzen der PIN: {e}")
        
        return