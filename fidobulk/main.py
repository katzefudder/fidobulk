import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import Fidobulk

import os
import configparser

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Running inside PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running in normal Python environment
        return os.path.join(os.path.abspath("."), relative_path)

def load_config(config_filename='config.ini'):
    config_path = get_resource_path(config_filename)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")

    config = configparser.ConfigParser()
    config.read(config_path)
    return config

if __name__ == "__main__":
    config_file = load_config()

    app = QApplication(sys.argv)
    window = Fidobulk(config=config_file)
    window.show()
    sys.exit(app.exec_())