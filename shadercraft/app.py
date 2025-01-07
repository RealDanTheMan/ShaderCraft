import sys
import os
from datetime import datetime
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

    os.makedirs("logs", exist_ok=True)
    timestamp: str = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    log_file: str = f"logs/shadercraft-{timestamp}.log"
    initLogger(file=log_file)
    Log.info(f"Log file created -> {log_file}")

    app: QApplication = QApplication(sys.argv)
    Log.info("Creaing app window")

    window = AppWindow()
    window.setStyleSheet(app_style)
    window.show()

    sys.exit(app.exec())
