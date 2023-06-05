import logging
from unittest import mock
from unittest.mock import MagicMock

import pytest
from hamcrest import assert_that, equal_to, contains_string
from tests.unit_test_utils import check_mocked_functions_called
from uitestcore.utilities.logger_handler import init_unique_log_file_logger, auto_log

test_class_name = "test_class"
return_value = "my return value"


@auto_log(test_class_name)
def dummy_method(throw_exception=False, do_logging=False, do_return=False):

    if throw_exception:
        raise ValueError("Throwing value exception as part of test")

    if do_logging:
        logger = logging.getLogger(test_class_name)
        logger.info("Test inner method log message")

    if do_return:
        return return_value

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

    assert_that(mock_logger.mock_calls[1][1][0], contains_string("Entering function %s"),
                "Expected to find entry message in logs")
    assert_that(mock_logger.mock_calls[1][1][1], contains_string("dummy_method"),
                "Expected to find method name in entry message in logs")
    assert_that(mock_logger.mock_calls[2][1][0], contains_string("Exited function %s"),
                "Expected to find exit message in logs")
    assert_that(mock_logger.mock_calls[2][1][1], contains_string("dummy_method"),
                "Expected to find method name in exit message in logs")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log_class_name_is_correct(mock_logging):

    dummy_method()
    mock_logging.getLogger.assert_called_once_with(test_class_name)


@mock.patch(__name__+".logging")
def test_auto_log_inner_function_logging(mock_test_logging):
    mock_test_logger = MagicMock(name="mock_test_logger")
    mock_test_logging.getLogger = mock_test_logger

    dummy_method(do_logging=True)

    assert_that(mock_test_logger.mock_calls[1][1][0], contains_string("Test inner method log message"),
                "Expected to find the logged message from inside the dummy_method function")
    assert_that(mock_test_logger.mock_calls[1][0], contains_string("info"),
                "Logged message from within function not logged at expected level")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log_exception_handling(mock_logging):
    mock_logger = MagicMock(name="mock_logger")
    mock_logging.getLogger = mock_logger

    with pytest.raises(ValueError) as excinfo:
        dummy_method(throw_exception=True)

    assert_that(str(excinfo.value), contains_string("Throwing value exception as part of test"),
                "Unexpected exception thrown")
    assert_that(mock_logger.mock_calls[1][1][0], contains_string("Entering function %s"),
                "Expected to find entry message in logs")
    assert_that(mock_logger.mock_calls[2][1][0],
                contains_string("There was an exception thrown in function %s"),
                "Expected to find exception thrown message from the auto_log decorator in logs")
    assert_that(mock_logger.mock_calls[2][1][1],
                contains_string("dummy_method"),
                "Expected to find method name in exception thrown message from the auto_log decorator in logs")
    assert_that(mock_logger.mock_calls[2][0], contains_string("exception"),
                "Exception log message not logged at expected level")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log_return_value(mock_logging):
    mock_logger = MagicMock(name="mock_logger")
    mock_logging.getLogger = mock_logger

    val_returned = dummy_method(do_return=True)

    assert_that(val_returned, equal_to(return_value))
    assert_that(mock_logger.mock_calls[2][1][0], contains_string(f"with return value %s"),
                "Expected to find return value in exit message in logs")
    assert_that(mock_logger.mock_calls[2][1][3], contains_string(return_value),
                "Expected to find return value in exit message in logs")


@mock.patch("uitestcore.utilities.logger_handler.logging")
def test_auto_log_none_return_value(mock_logging):
    mock_logger = MagicMock(name="mock_logger")
    mock_logging.getLogger = mock_logger

    val_returned = dummy_method(do_return=False)

    assert_that(val_returned, equal_to(None))
    assert_that(mock_logger.mock_calls[2][1][0], contains_string("with return value %s"),
                "Expected to find blank return value in exit message in logs")
    assert_that(mock_logger.mock_calls[2][1][3], equal_to(None),
                "Expected to find blank return value in exit message in logs")
