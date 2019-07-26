from datetime import datetime
from unittest import mock
from hamcrest import equal_to
from tests.unit.unit_test_utils import *
from ui_automation_core.utilities.browser_handler import *


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


class MockContext:
    def __init__(self, maximize_browser=None, logging_flag=None, implicit_wait=0):
        self.maximize_browser = maximize_browser
        self.logging_flag = logging_flag
        self.browser = MockBrowser()
        self.logger = MockLogger()
        self.implicit_wait = implicit_wait


class MockConfig:
    def __init__(self, userdata=None):
        self.userdata = userdata


class MockLogger:
    def __init__(self, disabled=False, log_file_exists=False):
        self.disabled = disabled
        self.log_file_exists = log_file_exists

    @staticmethod
    def create_log_file():
        return MockLogger(False, True)


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


class MockBuiltIn:

    def __init__(self, *args):
        pass

    def __enter__(self, *args):
        return "data"

    def __exit__(self, *args):
        pass


browserstack_data = {
    "CONFIG_FILE": "test.json",
    "TASK_ID": 0,
    "BROWSERSTACK_USERNAME": "test_user",
    "BROWSERSTACK_ACCESS_KEY": "1234"
}

browserstack_config = {
    "environments": [{}],
    "capabilities": {
        "cap1": "1",
        "cap2": "2",
        "cap3": "3"
    },
    "server": "test_server"
}


def test_set_browser_size_maximized():
    context = MockContext(maximize_browser=True)

    BrowserHandler.set_browser_size(context)

    assert_that(context.browser.browser_is_maximised, "Browser was not maximized")


def test_set_browser_size_not_maximized():
    context = MockContext(maximize_browser=False)

    BrowserHandler.set_browser_size(context)

    assert_that(not context.browser.browser_is_maximised, "Browser was maximized but should not be")


@mock.patch("ui_automation_core.utilities.logger.Logger.create_log_file",
            side_effect=MockLogger.create_log_file)
def test_prepare_browser_enable_logger(mock_create_log_file):
    context = MockContext(logging_flag=True)
    context.config = MockConfig()

    BrowserHandler.prepare_browser(context)

    check_mocked_functions_called(mock_create_log_file)
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
def test_take_screenshot_save_file(mock_get_current_datetime, mock_makedirs, mock_path_exists):
    driver = MockDriver(1024, 768, 2000)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called(mock_path_exists, mock_makedirs, mock_get_current_datetime)
    assert_that(driver.screenshot_filename, equal_to("screenshots/2019-02-15_00.00.00.000000_test_screenshot.png"),
                "The screenshot filename was incorrect")


@mock.patch("os.path.exists", side_effect=lambda *args: True)
def test_take_screenshot_resize_window(mock_path_exists):
    driver = MockDriver(1024, 768, 2000)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called(mock_path_exists)
    assert_that(driver.num_resizes, equal_to(2), "Window should have been resized for the screenshot and then reset")
    assert_that(driver.window_height, equal_to(768), "Window height should have been reverted to its original value")


@mock.patch("os.path.exists", side_effect=lambda *args: True)
def test_take_screenshot_no_resize_window(mock_path_exists):
    driver = MockDriver(1024, 768, 500)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called(mock_path_exists)
    assert_that(driver.num_resizes, equal_to(0), "Window should not have been resized")
    assert_that(driver.window_height, equal_to(768), "Window height should not have changed")


@mock.patch("os.listdir", side_effect=lambda *args: [])
@mock.patch("os.path.exists", side_effect=lambda *args: False)
@mock.patch("os.makedirs", side_effect=lambda *args: None)
def test_move_screenshots_to_folder_create_folder(mock_makedirs, mock_path_exists, mock_listdir):
    BrowserHandler.move_screenshots_to_folder("test_folder")

    check_mocked_functions_called(mock_listdir, mock_path_exists, mock_makedirs)
    mock_makedirs.assert_called_with("screenshots/test_folder")


@mock.patch("os.listdir", side_effect=lambda *args: [])
@mock.patch("os.path.exists", side_effect=lambda *args: True)
@mock.patch("os.makedirs", side_effect=lambda *args: None)
def test_move_screenshots_to_folder_do_not_create_folder(mock_makedirs, mock_path_exists, mock_listdir):
    BrowserHandler.move_screenshots_to_folder("test_folder")

    check_mocked_functions_called(mock_listdir, mock_path_exists)
    check_mocked_functions_not_called(mock_makedirs)


@mock.patch("os.listdir", side_effect=lambda *args: ["test1.png", "test2.jpg", "test3.png", "test4.png", "test5.bmp"])
@mock.patch("os.path.exists", side_effect=lambda *args: True)
@mock.patch("shutil.move", side_effect=lambda *args: None)
def test_move_screenshots_to_folder(mock_move, mock_path_exists, mock_listdir):
    BrowserHandler.move_screenshots_to_folder("test_folder")

    check_mocked_functions_called(mock_listdir, mock_path_exists, mock_move)
    assert_that(mock_move.call_count, equal_to(3), "Only .png files should be moved")
    mock_move.assert_any_call("screenshots/test1.png", "screenshots/test_folder")
    mock_move.assert_any_call("screenshots/test3.png", "screenshots/test_folder")
    mock_move.assert_any_call("screenshots/test4.png", "screenshots/test_folder")


def test_parse_config_data_false_values():
    userdata = {
        "logging_flag": "false",
        "maximize_browser_flag": "false",
    }
    context = MockContext()
    context.config = MockConfig(userdata)

    parse_config_data(context)

    assert_that(context.logging_flag, equal_to(False), "Logging flag should be false")
    assert_that(context.maximize_browser, equal_to(False), "Maximize browser should be false")


def test_parse_config_data_true_values():
    userdata = {
        "logging_flag": "true",
        "maximize_browser_flag": "true",
    }
    context = MockContext()
    context.config = MockConfig(userdata)

    parse_config_data(context)

    assert_that(context.logging_flag, equal_to(True), "Logging flag should be true")
    assert_that(context.maximize_browser, equal_to(True), "Maximize browser should be true")


@mock.patch("ui_automation_core.utilities.browser_handler.open_browser", side_effect=lambda *args: None)
def test_parse_config_data_opens_browser_with_url(mock_open_browser):
    base_url = "https://www.nhs.uk"
    userdata = {
        "base_url": base_url,
        "browser": "chrome"
    }
    context = MockContext()
    context.config = MockConfig(userdata)

    parse_config_data(context)

    check_mocked_functions_called(mock_open_browser)
    opened_url = mock_open_browser.call_args[0][0].url
    assert_that(opened_url, equal_to(base_url), "Browser opened with incorrect url")


@mock.patch("ui_automation_core.utilities.browser_handler.open_chrome", side_effect=lambda *args: None)
@mock.patch("ui_automation_core.utilities.browser_handler.start_browserstack", side_effect=lambda *args: None)
def test_open_browser_chrome(mock_start_browserstack, mock_open_chrome):
    context = MockContext()
    context.browser.name = "chrome"

    open_browser(context)

    check_mocked_functions_called(mock_open_chrome)
    check_mocked_functions_not_called(mock_start_browserstack)


@mock.patch("ui_automation_core.utilities.browser_handler.open_chrome", side_effect=lambda *args: None)
@mock.patch("ui_automation_core.utilities.browser_handler.start_browserstack", side_effect=lambda *args: None)
def test_open_browser_browserstack(mock_start_browserstack, mock_open_chrome):
    context = MockContext()
    context.browser.name = "browserstack"

    open_browser(context)

    check_mocked_functions_called(mock_start_browserstack)
    check_mocked_functions_not_called(mock_open_chrome)


@mock.patch("os.name", "nt")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("selenium.webdriver.ChromeOptions", side_effect=lambda *args: None)
@mock.patch("ui_automation_core.utilities.browser_handler.BrowserHandler.set_browser_size",
            side_effect=lambda *args: None)
def test_open_chrome_windows(mock_set_browser_size, mock_chromeoptions, mock_chrome):
    context = MockContext()

    open_chrome(context)

    check_mocked_functions_called(mock_chrome, mock_set_browser_size)
    check_mocked_functions_not_called(mock_chromeoptions)


@mock.patch("os.name", "ubuntu")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("selenium.webdriver.ChromeOptions.add_argument", side_effect=lambda *args: None)
@mock.patch("ui_automation_core.utilities.browser_handler.BrowserHandler.set_browser_size",
            side_effect=lambda *args: None)
def test_open_chrome_non_windows(mock_set_browser_size, mock_add_argument, mock_chrome):
    context = MockContext()

    open_chrome(context)

    assert_that(mock_add_argument.call_count, equal_to(4), "Incorrect number of arguments added to chrome")
    mock_add_argument.assert_any_call("--no-sandbox")
    mock_add_argument.assert_any_call("--window-size=1420,1080")
    mock_add_argument.assert_any_call("--headless")
    mock_add_argument.assert_any_call("--disable-gpu")
    check_mocked_functions_called(mock_chrome, mock_set_browser_size)


@mock.patch("os.environ", browserstack_data)
@mock.patch("ui_automation_core.utilities.browser_handler.open", side_effect=MockBuiltIn)
@mock.patch("json.load", side_effect=lambda *args: browserstack_config)
@mock.patch("selenium.webdriver.Remote", side_effect=lambda **kwargs: "mock_browserstack")
def test_start_browserstack(mock_remote, mock_load, mock_open):
    context = MockContext()

    start_browserstack(context)

    check_mocked_functions_called(mock_remote, mock_load, mock_open)
    mock_remote.assert_called_with(command_executor="http://test_user:1234@test_server/wd/hub",
                                   desired_capabilities={"cap1": "1", "cap2": "2", "cap3": "3"})