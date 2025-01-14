import os
import time
import unittest
from PySide6.QtWidgets import QApplication
from shadercraft.app import initLogger, main


class AppTest(unittest.TestCase):
    def test_logger_init(self) -> None:
        """
        Test application log initialisation.
        """
        log: str = "test_app.log"
        initLogger(file=log)

        assert os.path.exists(log), "App test failed, failed to initialise test logger."
        os.remove(log)
