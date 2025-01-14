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

    def testWindowLogging(self) -> None:
        """
        Tests window ability to log information to file on disk.
        """
        log_path: str = "test_logs"
        log_file: str = "test_logs/appwindow.log"
        os.makedirs(log_path, exist_ok=True)
        initLogger(log_file)
        win: AppWindow = AppWindow()
        win.show()

        Log.info("logging test information")
        Log.info("Logging more test information")
        time.sleep(win.log_refresh_rate * 0.001 + 1)

        assert win.getLogFile() is not None
        assert win.log_last_pos > 0, "Logging position is invalid"
        assert win.log_refresh_rate > 0, "Logging refresh rate is 0"

        win.close()
        del win
