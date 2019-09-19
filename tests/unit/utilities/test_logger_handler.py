import logging
from unittest import mock
from unittest.mock import MagicMock

import pytest
from hamcrest import assert_that, equal_to, contains_string
from tests.unit.unit_test_utils import check_mocked_functions_called
from uitestcore.utilities.logger_handler import init_unique_log_file_logger, auto_log

test_class_name = "test_class"


@auto_log(test_class_name)
def dummy_method(throw_exception=False, do_logging=False):

    if throw_exception:
        raise ValueError("Throwing value exception as part of test")

    if do_logging:
        logger = logging.getLogger(test_class_name)
        logger.info("Test inner method log message")

    # method itself doesn't need to do anything


@mock.patch("os.path.exists", side_effect=lambda *args: True)
@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_init_unique_log_file_logger(mock_logging, mock_path_exists):
    init_unique_log_file_logger()
    check_mocked_functions_called(mock_path_exists)
    assert_that(mock_logging.method_calls[0][0], contains_string("basicConfig"),
                "logger_handler isn't using basicConfig as expected")
    assert_that(mock_logging.method_calls[0][2]['level'], equal_to(20),
                "logger_handler default log level is not as expected")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_init_unique_log_file_logger_removes_root_handlers(mock_logging):
    mock_logging.root.handlers = ["handler_0"]
    init_unique_log_file_logger()
    mock_logging.root.removeHandler.assert_called_once()


@mock.patch("os.path.exists", side_effect=lambda *args: False)
@mock.patch("uitestcore.utilities.logger_handler.logging")
@mock.patch("os.makedirs")
def test_init_unique_log_file_logger_creates_folder(mock_makedirs, mock_logging, mock_path_exists):
    init_unique_log_file_logger("test/logs")
    check_mocked_functions_called(mock_makedirs, mock_path_exists)
    mock_makedirs.assert_called_with("test/logs")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log(mock_logging):
    mock_logger = MagicMock(name="mock_logger")
    mock_logging.getLogger = mock_logger

    dummy_method()
    mock_logging.getLogger.assert_called_once()

    assert_that(mock_logger.mock_calls[1][1][0], contains_string("Entering function dummy_method"),
                "Expected to find entry message in logs")
    assert_that(mock_logger.mock_calls[2][1][0], contains_string("Exited function dummy_method"),
                "Expected to find exit message in logs")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log_class_name_is_correct(mock_logging):

    dummy_method()
    mock_logging.getLogger.assert_called_once_with(test_class_name)


@mock.patch("tests.unit.utilities.test_logger_handler.logging")
@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log_inner_function_logging(mock_logging, mock_test_logging):
    mock_logger = MagicMock(name="mock_logger")
    mock_logging.getLogger = mock_logger
    mock_test_logging.getLogger = mock_logger

    dummy_method(do_logging=True)

    assert_that(mock_logger.mock_calls[3][1][0], contains_string("Test inner method log message"),
                "Expected to find the logged message from inside the dummy_method function")
    assert_that(mock_logger.mock_calls[3][0], contains_string("info"),
                "Logged message from within function not logged at expected level")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log_exception_handling(mock_logging):
    mock_logger = MagicMock(name="mock_logger")
    mock_logging.getLogger = mock_logger

    with pytest.raises(ValueError) as excinfo:
        dummy_method(throw_exception=True)

    assert_that(str(excinfo.value), contains_string("Throwing value exception as part of test"),
                "Unexpected exception thrown")
    assert_that(mock_logger.mock_calls[1][1][0], contains_string("Entering function dummy_method"),
                "Expected to find entry message in logs")
    assert_that(mock_logger.mock_calls[2][1][0],
                contains_string("There was an exception thrown in function dummy_method"),
                "Expected to find exception thrown message from the auto_log decorator in logs")
    assert_that(mock_logger.mock_calls[2][0], contains_string("exception"),
                "Exception log message not logged at expected level")
