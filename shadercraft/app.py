import sys
from PySide6.QtWidgets import QApplication
from .appwindow import AppWindow


def Main() -> int:
    print('Starting Shadercraft')

    app = QApplication(sys.argv)

    window = AppWindow()
    window.show()

    sys.exit(app.exec())

