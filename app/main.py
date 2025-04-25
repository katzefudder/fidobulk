import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import YkBatch

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YkBatch()
    window.show()
    sys.exit(app.exec_())
