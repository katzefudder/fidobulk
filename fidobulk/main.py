import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import Fidobulk

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Fidobulk()
    window.show()
    sys.exit(app.exec_())
