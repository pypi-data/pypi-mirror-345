import pytest
from debugg_ai_sdk.logger import Logger

def test_logger_creation():
    logger = Logger("test_logger")
    assert logger.logger.name == "test_logger"

def test_log_info():
    logger = Logger("test_logger")
    # Test if logging doesn't throw error
    logger.info("Test info log")
