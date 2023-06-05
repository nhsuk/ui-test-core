import io
from datetime import datetime
from unittest import mock
from hamcrest import equal_to, raises, calling
from tests.unit_test_utils import *
from uitestcore.utilities.browser_handler import *


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
    def __init__(self, maximize_browser=None, logging_flag=None, implicit_wait=0, browser_options=None):
        self.maximize_browser = maximize_browser
        self.logging_flag = logging_flag
        self.browser = MockBrowser()
        self.browser_options = browser_options
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
    def __init__(self, window_width, window_height, scroll_height, save_screenshot_success=True):
        self.window_width = window_width
        self.window_height = window_height
        self.scroll_height = scroll_height
        self.save_screenshot_success = save_screenshot_success
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
        return self.save_screenshot_success


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


@mock.patch("uitestcore.utilities.browser_handler.parse_config_data")
@mock.patch("uitestcore.utilities.browser_handler.open_browser")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_prepare_browser(mock_set_browser_size, mock_open_browser, mock_parse_config_data):
    context = MockContext(implicit_wait=10)

    BrowserHandler.prepare_browser(context)

    mock_parse_config_data.assert_called_once_with(context)
    mock_open_browser.assert_called_once_with(context)
    mock_set_browser_size.assert_called_once_with(context)
    assert_that(context.browser.implicit_wait, equal_to(10), "Implicit wait not set correctly")


@mock.patch("os.path.exists", side_effect=lambda *args: False)
@mock.patch("os.makedirs")
@mock.patch("uitestcore.utilities.browser_handler.get_current_datetime",
            side_effect=lambda *args: datetime.strptime("2019-02-15_00.00.00.000000", "%Y-%m-%d_%H.%M.%S.%f"))
def test_take_screenshot_save_file_success(mock_get_current_datetime, mock_makedirs, mock_path_exists):
    driver = MockDriver(1024, 768, 2000, True)

    result = BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called(mock_path_exists, mock_makedirs, mock_get_current_datetime)
    assert_that(driver.screenshot_filename, equal_to("screenshots/2019-02-15_00.00.00.000000_test_screenshot.png"),
                "The screenshot filename was incorrect")
    assert_that(result, equal_to(True), "The screenshot should have been saved successfully")


def test_take_screenshot_save_file_fail():
    driver = MockDriver(1024, 768, 2000, False)

    result = BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called()
    assert_that(result, equal_to(False), "The screenshot should have failed to save")


@mock.patch("os.path.exists", side_effect=lambda *args: False)
@mock.patch("os.makedirs")
@mock.patch("uitestcore.utilities.browser_handler.get_current_datetime",
            side_effect=lambda *args: datetime.strptime("2019-02-15_00.00.00.000000", "%Y-%m-%d_%H.%M.%S.%f"))
def test_take_screenshot_save_file_with_invalid_characters(mock_get_current_datetime, mock_makedirs, mock_path_exists):
    driver = MockDriver(1024, 768, 2000)

    BrowserHandler.take_screenshot(driver, "abc://test_screenshot")

    check_mocked_functions_called(mock_path_exists, mock_makedirs, mock_get_current_datetime)
    assert_that(driver.screenshot_filename, equal_to("screenshots/2019-02-15_00.00.00.000000_abc__test_screenshot.png"),
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
@mock.patch("os.makedirs")
def test_move_screenshots_to_folder_create_folder(mock_makedirs, mock_path_exists, mock_listdir):
    BrowserHandler.move_screenshots_to_folder("test_folder")

    check_mocked_functions_called(mock_listdir, mock_path_exists, mock_makedirs)
    mock_makedirs.assert_called_with("screenshots/test_folder")


@mock.patch("os.listdir", side_effect=lambda *args: [])
@mock.patch("os.path.exists", side_effect=lambda *args: True)
@mock.patch("os.makedirs")
def test_move_screenshots_to_folder_do_not_create_folder(mock_makedirs, mock_path_exists, mock_listdir):
    BrowserHandler.move_screenshots_to_folder("test_folder")

    check_mocked_functions_called(mock_listdir, mock_path_exists)
    check_mocked_functions_not_called(mock_makedirs)


@mock.patch("os.listdir", side_effect=lambda *args: ["test1.png", "test2.jpg", "test3.png", "test4.png", "test5.bmp"])
@mock.patch("os.path.exists", side_effect=lambda *args: True)
@mock.patch("shutil.move")
def test_move_screenshots_to_folder(mock_move, mock_path_exists, mock_listdir):
    BrowserHandler.move_screenshots_to_folder("test_folder")

    check_mocked_functions_called(mock_listdir, mock_path_exists, mock_move)
    assert_that(mock_move.call_count, equal_to(3), "Only .png files should be moved")
    mock_move.assert_any_call("screenshots/test1.png", "screenshots/test_folder")
    mock_move.assert_any_call("screenshots/test3.png", "screenshots/test_folder")
    mock_move.assert_any_call("screenshots/test4.png", "screenshots/test_folder")


@mock.patch("uitestcore.utilities.browser_handler.open_chrome")
@mock.patch("uitestcore.utilities.browser_handler.open_edge")
@mock.patch("uitestcore.utilities.browser_handler.start_browserstack")
@mock.patch("uitestcore.utilities.browser_handler.open_firefox")
def test_open_browser_chrome(mock_open_firefox, mock_start_browserstack, mock_open_edge, mock_open_chrome):
    context = MockContext()
    context.browser_name = "chrome"

    open_browser(context)

    check_mocked_functions_called(mock_open_chrome)
    check_mocked_functions_not_called(mock_open_firefox, mock_start_browserstack, mock_open_edge)


@mock.patch("uitestcore.utilities.browser_handler.open_chrome")
@mock.patch("uitestcore.utilities.browser_handler.open_edge")
@mock.patch("uitestcore.utilities.browser_handler.start_browserstack")
@mock.patch("uitestcore.utilities.browser_handler.open_firefox")
def test_open_browser_edge(mock_open_firefox, mock_start_browserstack, mock_open_edge, mock_open_chrome):
    context = MockContext()
    context.browser_name = "edge"

    open_browser(context)

    check_mocked_functions_called(mock_open_edge)
    check_mocked_functions_not_called(mock_open_firefox, mock_start_browserstack, mock_open_chrome)


@mock.patch("uitestcore.utilities.browser_handler.open_chrome")
@mock.patch("uitestcore.utilities.browser_handler.open_edge")
@mock.patch("uitestcore.utilities.browser_handler.start_browserstack")
@mock.patch("uitestcore.utilities.browser_handler.open_firefox")
def test_open_browser_firefox(mock_open_firefox, mock_start_browserstack, mock_open_edge, mock_open_chrome):
    context = MockContext()
    context.browser_name = "firefox"

    open_browser(context)

    check_mocked_functions_called(mock_open_firefox)
    check_mocked_functions_not_called(mock_open_chrome, mock_start_browserstack, mock_open_edge)


@mock.patch("uitestcore.utilities.browser_handler.open_chrome")
@mock.patch("uitestcore.utilities.browser_handler.open_edge")
@mock.patch("uitestcore.utilities.browser_handler.start_browserstack")
@mock.patch("uitestcore.utilities.browser_handler.open_firefox")
def test_open_browser_browserstack(mock_open_firefox, mock_start_browserstack, mock_open_edge, mock_open_chrome):
    context = MockContext()
    context.browser_name = "browserstack"

    open_browser(context)

    check_mocked_functions_called(mock_start_browserstack)
    check_mocked_functions_not_called(mock_open_chrome, mock_open_firefox, mock_open_edge)


@mock.patch("uitestcore.utilities.browser_handler.open_chrome")
@mock.patch("uitestcore.utilities.browser_handler.open_edge")
@mock.patch("uitestcore.utilities.browser_handler.start_browserstack")
@mock.patch("uitestcore.utilities.browser_handler.open_firefox")
def test_open_browser_not_supported(mock_open_firefox, mock_start_browserstack, mock_open_edge, mock_open_chrome):
    context = MockContext()
    context.browser_name = "ie"

    assert_that(calling(open_browser).with_args(context), raises(ValueError),
                "A ValueError should occur when the desired browser is not supported")

    check_mocked_functions_not_called(mock_open_chrome, mock_open_edge, mock_start_browserstack, mock_open_firefox)


@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_chrome_browser_options_not_defined(mock_set_browser_size, mock_chrome, mock_platform, mock_stdout):
    context = MockContext()
    delattr(context, "browser_options")

    open_chrome(context)

    assert_that(mock_stdout.getvalue(), equal_to(
        "No config browser_options detected and the variable 'context.browser_options' is not defined\n"),
                "Unexpected print string")
    check_mocked_functions_called(mock_chrome, mock_set_browser_size)


@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("selenium.webdriver.ChromeOptions.add_argument")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_chrome_windows_os_options(mock_set_browser_size, mock_add_argument, mock_chrome, mock_platform):
    context = MockContext()
    context.browser_options = ["--headless"]

    open_chrome(context)

    assert_that(mock_add_argument.call_count, equal_to(1), "Incorrect number of arguments added to chrome")
    mock_add_argument.assert_any_call("--headless")
    check_mocked_functions_called(mock_chrome, mock_set_browser_size)


@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("selenium.webdriver.ChromeOptions")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_chrome_windows_os(mock_set_browser_size, mock_chromeoptions, mock_chrome, mock_platform):
    context = MockContext()

    open_chrome(context)

    check_mocked_functions_called(mock_chrome, mock_set_browser_size, mock_chromeoptions)


@mock.patch("platform.system", return_value="Darwin")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("selenium.webdriver.ChromeOptions")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_chrome_mac_os(mock_set_browser_size, mock_chromeoptions, mock_chrome, mock_platform):
    context = MockContext()

    open_chrome(context)

    check_mocked_functions_called(mock_chrome, mock_set_browser_size, mock_chromeoptions)


@mock.patch("platform.system", return_value="Linux")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("selenium.webdriver.ChromeOptions.add_argument")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_chrome_non_windows_os_options(mock_set_browser_size, mock_add_argument, mock_chrome, mock_platform):
    context = MockContext()
    context.browser_options = ["--ignore-certificate-errors"]

    open_chrome(context)

    assert_that(mock_add_argument.call_count, equal_to(5), "Incorrect number of arguments added to chrome")
    mock_add_argument.assert_any_call("--no-sandbox")
    mock_add_argument.assert_any_call("--window-size=1420,1080")
    mock_add_argument.assert_any_call("--headless")
    mock_add_argument.assert_any_call("--disable-gpu")
    mock_add_argument.assert_any_call("--ignore-certificate-errors")
    check_mocked_functions_called(mock_chrome, mock_set_browser_size)


@mock.patch("platform.system", return_value="Linux")
@mock.patch("selenium.webdriver.Chrome", side_effect=lambda **kwargs: "mock_chrome")
@mock.patch("selenium.webdriver.ChromeOptions.add_argument")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_chrome_non_windows_os(mock_set_browser_size, mock_add_argument, mock_chrome, mock_platform):
    context = MockContext()

    open_chrome(context)

    assert_that(mock_add_argument.call_count, equal_to(4), "Incorrect number of arguments added to chrome")
    mock_add_argument.assert_any_call("--no-sandbox")
    mock_add_argument.assert_any_call("--window-size=1420,1080")
    mock_add_argument.assert_any_call("--headless")
    mock_add_argument.assert_any_call("--disable-gpu")
    check_mocked_functions_called(mock_chrome, mock_set_browser_size)


@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch("platform.system", return_value="Darwin")
@mock.patch("selenium.webdriver.Edge", side_effect=lambda **kwargs: "mock_edge")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_edge_browser_options_not_defined(mock_set_browser_size, mock_edge, mock_platform, mock_stdout):
    context = MockContext()
    delattr(context, "browser_options")

    open_edge(context)

    assert_that(mock_stdout.getvalue(), equal_to(
        "No config browser_options detected and the variable 'context.browser_options' is not defined\n"),
                "Unexpected print string")
    check_mocked_functions_called(mock_edge, mock_set_browser_size)


@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Edge", side_effect=lambda **kwargs: "mock_edge")
@mock.patch("selenium.webdriver.EdgeOptions.add_argument")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_edge_windows_os_options(mock_set_browser_size, mock_add_argument, mock_edge, mock_platform):
    context = MockContext()
    context.browser_options = ["--headless"]

    open_edge(context)

    assert_that(mock_add_argument.call_count, equal_to(1), "Incorrect number of arguments added to edge")
    mock_add_argument.assert_any_call("--headless")
    check_mocked_functions_called(mock_edge, mock_set_browser_size)


@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Edge", side_effect=lambda **kwargs: "mock_edge")
@mock.patch("selenium.webdriver.EdgeOptions")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_edge_windows_os(mock_set_browser_size, mock_edgeoptions, mock_edge, mock_platform):
    context = MockContext()

    open_edge(context)

    check_mocked_functions_called(mock_edge, mock_set_browser_size, mock_edgeoptions)


@mock.patch("platform.system", return_value="Darwin")
@mock.patch("selenium.webdriver.Edge", side_effect=lambda **kwargs: "mock_edge")
@mock.patch("selenium.webdriver.EdgeOptions")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_edge_mac_os(mock_set_browser_size, mock_edgeoptions, mock_edge, mock_platform):
    context = MockContext()

    open_edge(context)

    check_mocked_functions_called(mock_edge, mock_set_browser_size, mock_edgeoptions)


@mock.patch("platform.system", return_value="Linux")
@mock.patch("selenium.webdriver.Edge", side_effect=lambda **kwargs: "mock_edge")
@mock.patch("selenium.webdriver.EdgeOptions.add_argument")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_edge_non_windows_os(mock_set_browser_size, mock_add_argument, mock_edge, mock_platform):
    context = MockContext()

    open_edge(context)

    assert_that(mock_add_argument.call_count, equal_to(4), "Incorrect number of arguments added to edge")
    mock_add_argument.assert_any_call("--no-sandbox")
    mock_add_argument.assert_any_call("--window-size=1420,1080")
    mock_add_argument.assert_any_call("--headless")
    mock_add_argument.assert_any_call("--disable-gpu")
    check_mocked_functions_called(mock_edge, mock_set_browser_size)


@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Firefox", side_effect=lambda **kwargs: "mock_firefox")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_firefox_browser_options_not_defined(mock_set_browser_size, mock_firefox, mock_platform, mock_stdout):
    context = MockContext()
    delattr(context, "browser_options")

    open_firefox(context)

    assert_that(mock_stdout.getvalue(), equal_to(
        "No config browser_options detected and the variable 'context.browser_options' is not defined\n"),
                "Unexpected print string")
    check_mocked_functions_called(mock_firefox, mock_set_browser_size)


@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Firefox", side_effect=lambda **kwargs: "mock_firefox")
@mock.patch("selenium.webdriver.FirefoxOptions.add_argument")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_firefox_windows_os_options(mock_set_browser_size, mock_add_argument, mock_firefox, mock_platform):
    context = MockContext()
    context.browser_options = ["--headless"]

    open_firefox(context)

    assert_that(mock_add_argument.call_count, equal_to(1), "Incorrect number of arguments added to firefox")
    mock_add_argument.assert_any_call("--headless")
    check_mocked_functions_called(mock_firefox, mock_set_browser_size)


@mock.patch("platform.system", return_value="Windows")
@mock.patch("selenium.webdriver.Firefox", side_effect=lambda **kwargs: "mock_firefox")
@mock.patch("selenium.webdriver.FirefoxOptions")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_firefox_windows_os(mock_set_browser_size, mock_firefoxoptions, mock_firefox, mock_platform):
    context = MockContext()

    open_firefox(context)

    check_mocked_functions_called(mock_firefox, mock_set_browser_size, mock_firefoxoptions)


@mock.patch("platform.system", return_value="Darwin")
@mock.patch("selenium.webdriver.Firefox", side_effect=lambda **kwargs: "mock_firefox")
@mock.patch("selenium.webdriver.FirefoxOptions")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_firefox_mac_os(mock_set_browser_size, mock_firefoxoptions, mock_firefox, mock_platform):
    context = MockContext()

    open_firefox(context)

    check_mocked_functions_called(mock_firefox, mock_set_browser_size, mock_firefoxoptions)


@mock.patch("platform.system", return_value="Linux")
@mock.patch("selenium.webdriver.Firefox", side_effect=lambda **kwargs: "mock_firefox")
@mock.patch("selenium.webdriver.FirefoxOptions.add_argument")
@mock.patch("uitestcore.utilities.browser_handler.BrowserHandler.set_browser_size")
def test_open_firefox_non_windows_os(mock_set_browser_size, mock_add_argument, mock_firefox, mock_platform):
    context = MockContext()

    open_firefox(context)

    assert_that(mock_add_argument.call_count, equal_to(1), "Incorrect number of arguments added to firefox")
    mock_add_argument.assert_any_call("--headless")
    check_mocked_functions_called(mock_firefox, mock_set_browser_size)


@mock.patch("os.environ", browserstack_data)
@mock.patch("uitestcore.utilities.browser_handler.open", side_effect=MockBuiltIn)
@mock.patch("json.load", side_effect=lambda *args: browserstack_config)
@mock.patch("selenium.webdriver.Remote", side_effect=lambda **kwargs: "mock_browserstack")
def test_start_browserstack(mock_remote, mock_load, mock_open):
    context = MockContext()

    start_browserstack(context)

    check_mocked_functions_called(mock_remote, mock_load, mock_open)
    mock_remote.assert_called_with(command_executor="https://test_user:1234@test_server/wd/hub",
                                   desired_capabilities={"cap1": "1", "cap2": "2", "cap3": "3"})
