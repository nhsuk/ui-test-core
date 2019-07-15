from datetime import datetime
from unittest import mock
from hamcrest import equal_to
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


# Mock webdriver object
class MockDriver(object):
    def __init__(self, window_width, window_height, scroll_height):
        self.window_width = window_width
        self.window_height = window_height
        self.scroll_height = scroll_height
        self.screenshot_filename = ""
        self.num_resizes = 0

    def get_window_size(self):
        return {
            "width": self.window_width,
            "height": self.window_height
        }

    def set_window_size(self, width, height):
        self.window_width = width
        self.window_height = height
        self.num_resizes += 1

    def execute_script(self, _script):
        return self.scroll_height

    def save_screenshot(self, file_name):
        self.screenshot_filename = file_name


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


@mock.patch("os.path.exists", side_effect=lambda *args: False)
@mock.patch("os.makedirs", side_effect=lambda *args: None)
@mock.patch("ui_automation_core.utilities.browser_handler.get_current_datetime",
            side_effect=lambda *args: datetime.strptime("2019-02-15_00.00.00.000000", "%Y-%m-%d_%H.%M.%S.%f"))
def test_take_screenshot_save_file(mock_path_exists, mock_makedirs, mock_get_current_datetime):
    driver = MockDriver(1024, 768, 2000)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_function_called(mock_path_exists)
    check_mocked_function_called(mock_makedirs)
    check_mocked_function_called(mock_get_current_datetime)
    assert_that(driver.screenshot_filename, equal_to("screenshots/2019-02-15_00.00.00.000000_test_screenshot.png"),
                "The screenshot filename was incorrect")


@mock.patch("os.path.exists", side_effect=lambda *args: True)
def test_take_screenshot_resize_window(mock_path_exists):
    driver = MockDriver(1024, 768, 2000)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_function_called(mock_path_exists)
    assert_that(driver.num_resizes, equal_to(2), "Window should have been resized for the screenshot and then reset")
    assert_that(driver.window_height, equal_to(768), "Window height should have been reverted to its original value")


@mock.patch("os.path.exists", side_effect=lambda *args: True)
def test_take_screenshot_no_resize_window(mock_path_exists):
    driver = MockDriver(1024, 768, 500)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_function_called(mock_path_exists)
    assert_that(driver.num_resizes, equal_to(0), "Window should not have been resized")
    assert_that(driver.window_height, equal_to(768), "Window height should not have changed")

