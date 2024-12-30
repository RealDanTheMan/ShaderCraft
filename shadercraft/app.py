import sys
from PySide6.QtWidgets import QApplication

from .appwindow import AppWindow
from .styles import app_style

def main() -> int:
    """Main entry point to the application"""
    print('Starting Shadercraft')

    app = QApplication(sys.argv)

    window = AppWindow()
    window.setStyleSheet(app_style)
    window.show()

    sys.exit(app.exec())
