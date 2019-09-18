from unittest import mock
from hamcrest import assert_that, equal_to, contains_string
from tests.unit.unit_test_utils import check_mocked_functions_called
from uitestcore.utilities.logger_handler import init_unique_log_file_logger


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
