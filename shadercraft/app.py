import sys
import logging as Log
from PySide6.QtWidgets import QApplication

from .asserts import assertRef
from .appwindow import AppWindow
from .styles import app_style

def initLogger(level=Log.DEBUG, file: str = "app.log"):
    """Initialise main app logger"""
    assertRef(level)
    assertRef(file)

    Log.basicConfig(
        level = level,
        format = "%(asctime)s - %(levelname)s - %(message)s",
        handlers = [
            Log.FileHandler(file),
            Log.StreamHandler()
        ]
    )

def main() -> int:
    """Main entry point to the application"""
    print('Starting Shadercraft')

    app: QApplication = QApplication(sys.argv)
    log_file: str = "shadercraft.log"
    initLogger(file=log_file)
    
    Log.info(f"Log file created -> {log_file}")
    Log.info("Creaing app window")

    window = AppWindow()
    window.setStyleSheet(app_style)
    window.show()

    sys.exit(app.exec())
