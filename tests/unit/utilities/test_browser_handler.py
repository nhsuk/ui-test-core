from unittest import mock
from tests.unit.unit_test_utils import *
from ui_automation_core.utilities.browser_handler import BrowserHandler


# Mock browser object
class MockBrowser:
    def __init__(self, browser_is_maximised=None, name="Test", implicit_wait=0):
        self.browser_is_maximised = browser_is_maximised
        self.name = name
        self.implicit_wait = implicit_wait

    def maximize_window(self):
        self.browser_is_maximised = True

    def lower(self):
        return self.name.lower()

    def implicitly_wait(self, implicit_wait):
        self.implicit_wait = implicit_wait


# Mock context object
class MockContext:
    def __init__(self, maximize_browser=None, logging_flag=False, implicit_wait=0):
        self.maximize_browser = maximize_browser
        self.logging_flag = logging_flag
        self.browser = MockBrowser()
        self.logger = MockLogger()
        self.implicit_wait = implicit_wait


# Mock config object
class MockConfig:
    def __init__(self, userdata=None):
        self.userdata = userdata


# Mock logger object
class MockLogger:
    def __init__(self, disabled=False, log_file_exists=False):
        self.disabled = disabled
        self.log_file_exists = log_file_exists

    @staticmethod
    def create_log_file():
        return MockLogger(False, True)


def test_set_browser_size_maximized():
    context = MockContext(maximize_browser=True)

    BrowserHandler.set_browser_size(context)

    assert_that(context.browser.browser_is_maximised, "Browser was not maximized")


def test_set_browser_size_not_maximized():
    context = MockContext(maximize_browser=False)

    BrowserHandler.set_browser_size(context)

    assert_that(not context.browser.browser_is_maximised, "Browser was maximized but should not be")


@mock.patch("ui_automation_core.utilities.browser_handler.Logger.create_log_file",
            side_effect=MockLogger.create_log_file)
def test_prepare_browser_enable_logger(mock_create_log_file):
    context = MockContext(logging_flag=True)
    context.config = MockConfig()

    BrowserHandler.prepare_browser(context)

    check_mocked_function_called(mock_create_log_file)
    assert_that(not context.logger.disabled, "The logger was disabled")
    assert_that(context.logger.log_file_exists, "The log file was not created")


def test_prepare_browser_disable_logger():
    context = MockContext(logging_flag=False)
    context.config = MockConfig()

    BrowserHandler.prepare_browser(context)

    assert_that(context.logger.disabled, "The logger was enabled")
    assert_that(not context.logger.log_file_exists, "The log file was created")
