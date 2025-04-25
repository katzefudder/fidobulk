from ykman import scripting as s

def get_serial_number():
    device = s.single()
    serial = device.info.serial
    if serial is None:
        raise ValueError("Serial number not available.")
    return serial
