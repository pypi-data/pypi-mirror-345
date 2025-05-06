# test_log_config.py
import re
import tempfile
import unittest
import logging
from pathlib import Path
import os
from commons.logging import config, get_logger


class TestLogConfig(unittest.TestCase):
    message_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} - \w+ \[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]: .+$"

    @classmethod
    def setUpClass(cls):
        cls.log_dir = Path(tempfile.mkdtemp())
        cls.log_file = cls.log_dir / "root.log"
        cls.logger = config(
            level=logging.DEBUG,
            directory=cls.log_dir,
            max_file_bytes=1024,
            backup_count=3,
            stream=None  # disable stdout
        )

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.log_file)
        os.rmdir(cls.log_dir)

    def test_logger_creation(self):
        logger = get_logger("TestLogger")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "TestLogger")

    def test_log_file_creation(self):
        self.logger.info("Test log message")
        self.assertTrue(self.log_file.exists())

    def test_log_level(self):
        logger = get_logger()
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        self.assertEqual(logger, self.logger)  # check if it is the root logger
        self.assertEqual(logger.level, logging.DEBUG)
        for log in self.log_file.read_text().splitlines():
            self.assertTrue(re.match(self.message_pattern, log))

    def test_global_logging_config(self):
        from logging.handlers import RotatingFileHandler

        self.assertEqual(self.logger.level, logging.DEBUG)
        self.assertTrue(
            any(isinstance(handler, RotatingFileHandler) for handler in self.logger.handlers))

    def test_custom_logger_config(self):
        custom_logger = get_logger(
            name="CustomLogger",
            level=logging.WARNING,
        )
        self.assertEqual(custom_logger.level, logging.WARNING)
        self.assertEqual(custom_logger.name, "CustomLogger")
