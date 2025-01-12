import sys
import os
from datetime import datetime
import logging as Log

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QSurfaceFormat

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
    os.environ["QT_OPENGL"] = "desktop"
    os.environ["QT_QPA_PLATFORM"] = "xcb"

    # Configure application logging
    os.makedirs("logs", exist_ok=True)
    timestamp: str = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    log_file: str = f"logs/shadercraft-{timestamp}.log"
    initLogger(file=log_file)
    Log.info(f"Log file created -> {log_file}")

    # Ensure correct OpenGL surface support for any OpenGL widgets
    # We use OpenGL widgets for our material preview renderer
    surface_format: QSurfaceFormat = QSurfaceFormat()
    surface_format.setVersion(4, 6)
    surface_format.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(surface_format)
    print(QSurfaceFormat.defaultFormat())

    # Create QT application and main app window
    app: QApplication = QApplication(sys.argv)
    Log.info("Creaing app window")

    window: AppWindow = AppWindow()
    window.setStyleSheet(app_style)
    window.show()
    window.preview_viewport.update()

    sys.exit(app.exec())

