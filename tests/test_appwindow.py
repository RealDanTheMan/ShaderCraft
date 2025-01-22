import os
import time
import unittest
import logging as Log
from PySide6.QtWidgets import QApplication

from shadercraft.app import initLogger
from shadercraft.appwindow import AppWindow


class AppWindowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app: QApplication = QApplication.instance() or QApplication([])

    def tearDown(self) -> None:
        self.app.quit()
        del self.app

    @staticmethod
    def freeLogs() -> None:
        for handler in Log.getLogger().handlers:
            handler.close()
            Log.getLogger().removeHandler(handler)

    def testWindowInit(self) -> None:
        """
        Test that all the main widnow along with the core widget initialised correctly.
        """
        win: AppWindow = AppWindow()
        win.show()

        assert win.ui is not None, "Failed to access base window template handle"
        assert win.palette_widget is not None, "Palette widget is not present in the main window"
        assert win.graph_view is not None, "Graph view is not present in the main window"
        assert win.graph_scene is not None, "Graph scene is not present in the main window"
        assert win.log_view is not None, "Log view panel is not present in the main window"
        assert win.property_panel is not None, "Property Panel is not present in the main widnow"
        assert win.preview_viewport is not None, "Preview Viewport is not present in the window"

        win.close()
        del win
        self.freeLogs()

    def testWindowLogging(self) -> None:
        """
        Tests window ability to log information to file on disk.
        """

        # Ensure logger is setup
        log_path: str = "logs/test/"
        log_file: str = "logs/test/test-appwindow.log"
        os.makedirs(log_path, exist_ok=True)
        initLogger(file=log_file)
        assert os.path.exists(log_file), "Log file not present on the disk"

        # Ensure window is setup
        win: AppWindow = AppWindow()
        win.show()

        # Check initial log fle state is valid
        assert win.getLogFile() is not None, "Log file bound to app window is None"
        assert win.getLogFile() != "/dev/null", "Log file bound to app window is dev/null"
        assert os.path.exists(win.getLogFile()), "Log file bound to app window is not on disk"

        # Log some test messages.
        Log.info(f"Test log initialised -> {log_file}")
        Log.debug("logging test debug message")
        Log.info("Logging test info message")
        Log.warning("Logging test warning message")
        Log.error("Logging test error message")

        # Flush all messages to disk
        time.sleep(1)
        for handler in Log.getLogger().handlers:
            print(f"Flushing log handler  ->  {handler}")
            handler.flush()

        # Logging view polls log file over portion oftime so we log some test info
        # and let some time pass before we sample state.
        self.app.processEvents()
        time.sleep(win.log_refresh_rate * 0.001)
        self.app.processEvents()
        time.sleep(win.log_refresh_rate * 0.001)
        self.app.processEvents()

        assert win.log_last_pos > 0, "Logging position is invalid"
        assert win.log_refresh_rate > 0, "Logging refresh rate is 0"

        # Test cleanup.
        win.close()
        del win
