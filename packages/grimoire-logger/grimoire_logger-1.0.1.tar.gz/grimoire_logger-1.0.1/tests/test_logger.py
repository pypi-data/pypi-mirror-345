import pytest
from unittest.mock import patch
import json
from datetime import datetime
from src.grimoire import Logger, LogLevel


@pytest.fixture
def logger():
    """Fixture to provide a Logger instance for each test."""
    return Logger()


def validate_log_format(log_str: str, expected_level: str, expected_message: str):
    """Helper function to validate log format."""
    log_dict = json.loads(log_str)
    assert "timestamp" in log_dict
    assert log_dict["level"] == expected_level
    assert log_dict["message"] == expected_message
    assert "source" in log_dict
    assert log_dict["source"].endswith(".py")
    # Validate timestamp format
    datetime.strptime(log_dict["timestamp"], "%Y-%m-%d %H:%M:%S")


@patch("builtins.print")
def test_info_logging(mock_print, logger):
    """Test info level logging."""
    test_message = "Test info message"
    logger.info(test_message)
    
    mock_print.assert_called_once()
    log_str = mock_print.call_args[0][0]
    validate_log_format(log_str, "info", test_message)


@patch("builtins.print")
def test_warn_logging(mock_print, logger):
    """Test warn level logging."""
    test_message = "Test warning message"
    logger.warn(test_message)
    
    mock_print.assert_called_once()
    log_str = mock_print.call_args[0][0]
    validate_log_format(log_str, "warn", test_message)


@patch("builtins.print")
def test_error_logging(mock_print, logger):
    """Test error level logging."""
    test_message = "Test error message"
    logger.error(test_message)
    
    mock_print.assert_called_once()
    log_str = mock_print.call_args[0][0]
    validate_log_format(log_str, "error", test_message)


@patch("builtins.print")
def test_debug_logging(mock_print, logger):
    """Test debug level logging with line number."""
    test_message = "Test debug message"
    logger.debug(test_message)
    
    mock_print.assert_called_once()
    log_str = mock_print.call_args[0][0]
    log_dict = json.loads(log_str)
    
    validate_log_format(log_str, "debug", test_message)
    assert "line" in log_dict


@patch("builtins.print")
def test_empty_message(mock_print, logger):
    """Test logging with empty message."""
    logger.info()
    
    mock_print.assert_called_once()
    log_str = mock_print.call_args[0][0]
    validate_log_format(log_str, "info", "")


def test_log_level_ordering():
    """Test that log levels have the expected ordering."""
    assert LogLevel.info.value < LogLevel.warn.value
    assert LogLevel.warn.value < LogLevel.error.value
    assert LogLevel.error.value < LogLevel.debug.value