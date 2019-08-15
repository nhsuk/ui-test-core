import logging
from unittest import mock
from hamcrest import assert_that, equal_to, is_, instance_of
from tests.unit.unit_test_utils import check_mocked_functions_called
from uitestcore.utilities.logger import Logger


class MockFileHandler:
    def __init__(self, filename):
        self.filename = filename
        self.level = None
        self.formatter = None
        self.log_record = None

    def setLevel(self, level):
        self.level = level

    def setFormatter(self, formatter):
        self.formatter = formatter

    def handle(self, log_record):
        self.log_record = log_record


@mock.patch("builtins.print")
def test_start(mock_print):
    Logger.start()

    mock_print.assert_called_with("Starting Test")


def test_init_logger():
    logger = Logger.init_logger()

    assert_that(logger.level, equal_to(logging.DEBUG), "Logger level incorrect")
    assert_that(logger.name, equal_to("base_logger"), "Logger name incorrect")


@mock.patch("os.path.exists", side_effect=lambda *args: True)
@mock.patch("logging.FileHandler", side_effect=MockFileHandler)
def test_create_log_file(mock_file_handler, mock_path_exists):
    logger = Logger.create_log_file()

    check_mocked_functions_called(mock_file_handler, mock_path_exists)
    assert_that(logger.handlers[0].log_record.message, equal_to("Created the file to write to"),
                "Log message incorrect or not found")
    assert_that(logger.handlers[0].level, equal_to(10), "File handler incorrect logging level")
    assert_that(logger.handlers[1].level, equal_to(40), "Stream handler incorrect logging level")
    assert_that(logger.handlers[0].formatter, is_(instance_of(logging.Formatter)), "File handler formatter not set")
    assert_that(logger.handlers[1].formatter, is_(instance_of(logging.Formatter)), "Stream handler formatter not set")


@mock.patch("os.path.exists", side_effect=lambda *args: False)
@mock.patch("logging.FileHandler", side_effect=MockFileHandler)
@mock.patch("os.makedirs")
@mock.patch("os.path.abspath", side_effect=lambda folder_name: "test/" + folder_name)
def test_create_log_file_creates_folder(mock_abspath, mock_makedirs, mock_file_handler, mock_path_exists):
    Logger.create_log_file()

    check_mocked_functions_called(mock_abspath, mock_makedirs, mock_file_handler, mock_path_exists)
    mock_makedirs.assert_called_with("test/logs")


@mock.patch("uitestcore.utilities.logger.logging.log")
def test_log(mock_log):
    Logger.log(20, "test message")

    mock_log.assert_called_with(20, "test message")
