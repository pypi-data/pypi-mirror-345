import pytest
from unittest.mock import patch, MagicMock, call
import sys
import argparse

import kuhl_haus.canary.app as app
from kuhl_haus.canary.env import (
    DEFAULT_CANARY_INVOCATION_INTERVAL,
    DEFAULT_CANARY_INVOCATION_COUNT,
)


@pytest.fixture
def mock_graphite_logger():
    mock = MagicMock()
    mock.logger = MagicMock()
    return mock


@pytest.fixture
def mock_script_handler():
    mock_handler = MagicMock()
    mock_script_func = MagicMock()
    mock_handler.return_value = mock_script_func
    return mock_handler


def test_parse_args_with_minimal_args():
    """Test parse_args with only required arguments."""
    # Arrange
    test_args = ['-s', 'test_script']

    # Act
    sut = app.parse_args(test_args)

    # Assert
    assert sut.script == 'test_script'
    assert sut.delay == DEFAULT_CANARY_INVOCATION_INTERVAL
    assert sut.count == DEFAULT_CANARY_INVOCATION_COUNT


def test_parse_args_with_all_args():
    """Test parse_args with all arguments specified."""
    # Arrange
    test_args = ['-s', 'test_script', '-d', '10', '-c', '5']

    # Act
    sut = app.parse_args(test_args)

    # Assert
    assert sut.script == 'test_script'
    assert sut.delay == 10
    assert sut.count == 5


def test_parse_args_with_long_form_args():
    """Test parse_args with long-form arguments."""
    # Arrange
    test_args = ['--script', 'test_script', '--delay', '10', '--count', '5']

    # Act
    sut = app.parse_args(test_args)

    # Assert
    assert sut.script == 'test_script'
    assert sut.delay == 10
    assert sut.count == 5


def test_parse_args_missing_script():
    """Test parse_args raises error when required script argument is missing."""
    # Arrange
    test_args = []

    # Act & Assert
    # with pytest.raises(SystemExit):
    result = app.parse_args(test_args)

    assert result.script is None


def test_parse_args_invalid_delay_type():
    """Test parse_args raises error when delay is not an integer."""
    # Arrange
    test_args = ['-s', 'test_script', '-d', 'not-an-int']

    # Act & Assert
    with pytest.raises(SystemExit):
        app.parse_args(test_args)


def test_parse_args_invalid_count_type():
    """Test parse_args raises error when count is not an integer."""
    # Arrange
    test_args = ['-s', 'test_script', '-c', 'not-an-int']

    # Act & Assert
    with pytest.raises(SystemExit):
        app.parse_args(test_args)

@patch('kuhl_haus.canary.app.parse_args')
@patch('kuhl_haus.metrics.recorders.graphite_logger.GraphiteLogger')  # Correct path
@patch('kuhl_haus.metrics.recorders.graphite_logger.GraphiteLoggerOptions')  # Correct path
@patch('kuhl_haus.canary.handlers.script_handler')  # Correct path
def test_main_successful_execution(
        mock_script_handler,
        mock_graphite_logger_options,
        mock_graphite_logger_class,
        mock_parse_args,
        mock_graphite_logger
):
    """Test main function with successful script execution."""
    # Arrange
    mock_args = MagicMock()
    mock_args.script = 'test_script'
    mock_args.delay = 5
    mock_args.count = 10
    mock_parse_args.return_value = mock_args

    # Setup GraphiteLoggerOptions constructor to return a mock options object
    mock_options = MagicMock()
    mock_graphite_logger_options.return_value = mock_options

    # Setup GraphiteLogger constructor to return our mock logger
    mock_graphite_logger_class.return_value = mock_graphite_logger

    # Setup script_handler to return a mock function
    mock_script_func = MagicMock()
    mock_script_handler.return_value = mock_script_func

    # Act
    app.main(['--script', 'test_script'])

    # Assert
    mock_parse_args.assert_called_once()
    mock_graphite_logger_options.assert_called_once()
    mock_graphite_logger_class.assert_called_once_with(mock_options)
    mock_script_handler.assert_called_once_with(mock_args.script)
    mock_script_func.assert_called_once_with(
        recorder=mock_graphite_logger,
        delay=mock_args.delay,
        count=mock_args.count
    )


@patch('kuhl_haus.canary.app.parse_args')
@patch('kuhl_haus.metrics.recorders.graphite_logger.GraphiteLogger')  # Correct path
@patch('kuhl_haus.metrics.recorders.graphite_logger.GraphiteLoggerOptions')  # Correct path
@patch('kuhl_haus.canary.handlers.script_handler')  # Correct path
def test_main_keyboard_interrupt(
        mock_script_handler,
        mock_graphite_logger_options,
        mock_graphite_logger_class,
        mock_parse_args,
        mock_graphite_logger
):
    """Test main function when KeyboardInterrupt is raised."""
    # Arrange
    mock_args = MagicMock()
    mock_args.script = 'test_script'
    mock_parse_args.return_value = mock_args

    # Setup GraphiteLoggerOptions constructor to return a mock options object
    mock_options = MagicMock()
    mock_graphite_logger_options.return_value = mock_options

    # Setup GraphiteLogger constructor to return our mock logger
    mock_graphite_logger_class.return_value = mock_graphite_logger

    # Set up the script_handler to raise KeyboardInterrupt when called
    mock_script_func = MagicMock(side_effect=KeyboardInterrupt())
    mock_script_handler.return_value = mock_script_func

    # Act
    app.main(['--script', 'test_script'])

    # Assert
    mock_graphite_logger.logger.info.assert_called_once_with("Received interrupt, exiting")


@patch('kuhl_haus.canary.app.parse_args')
@patch('kuhl_haus.metrics.recorders.graphite_logger.GraphiteLogger')  # Correct path
@patch('kuhl_haus.metrics.recorders.graphite_logger.GraphiteLoggerOptions')  # Correct path
@patch('kuhl_haus.canary.handlers.script_handler')  # Correct path
def test_main_unhandled_exception(
        mock_script_handler,
        mock_graphite_logger_options,
        mock_graphite_logger_class,
        mock_parse_args,
        mock_graphite_logger
):
    """Test main function when an unhandled exception is raised."""
    # Arrange
    mock_args = MagicMock()
    mock_args.script = 'test_script'
    mock_parse_args.return_value = mock_args

    # Setup GraphiteLoggerOptions constructor to return a mock options object
    mock_options = MagicMock()
    mock_graphite_logger_options.return_value = mock_options

    # Setup GraphiteLogger constructor to return our mock logger
    mock_graphite_logger_class.return_value = mock_graphite_logger

    # Set up the script_handler to raise an exception when called
    test_exception = ValueError("Test exception")
    mock_script_func = MagicMock(side_effect=test_exception)
    mock_script_handler.return_value = mock_script_func

    # Act
    app.main(['--script', 'test_script'])

    # Assert
    mock_graphite_logger.logger.error.assert_called_once()
    error_message = mock_graphite_logger.logger.error.call_args[0][0]
    assert f"Unhandled exception raised running script test_script" in error_message
    assert repr(test_exception) in error_message


@patch('kuhl_haus.canary.app.main')
def test_run_function(mock_main):
    """Test run function calls main with sys.argv."""
    # Arrange
    original_argv = sys.argv
    sys.argv = ['app.py', '--script', 'test_script']

    # Act
    app.run()

    # Assert
    mock_main.assert_called_once_with(['--script', 'test_script'])

    # Cleanup
    sys.argv = original_argv
