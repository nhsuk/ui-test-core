import io
from datetime import datetime
from unittest import mock
from unittest.mock import mock_open
from hamcrest import equal_to, raises, calling, not_, has_property, contains_string, has_length
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
    def __init__(self, maximize_browser=None, logging_flag=None, implicit_wait=0, browser_options=None,
                 scenario_name=None, axe=None):
        self.maximize_browser = maximize_browser
        self.logging_flag = logging_flag
        self.browser = MockBrowser()
        self.browser_options = browser_options
        self.logger = MockLogger()
        self.implicit_wait = implicit_wait
        if scenario_name is not None:
            self.scenario_name = scenario_name
        self.axe = axe


class MockAxe:
    def __init__(self, selenium=None):
        self.selenium = selenium

    @staticmethod
    def report(results_violations):
        return "\n".join(results_violations)


class MockSelenium:
    def __init__(self, title=None, capabilities_browser_name=None, capabilities_browser_version=None):
        self.title = title
        self.capabilities = {
            'browserName': capabilities_browser_name,
            'browserVersion': capabilities_browser_version
        }


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


class MockDriver:

    save_test_file = False

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
        if self.save_test_file:
            with open(file_name, "w+", encoding="UTF-8") as file:
                file.write("Test file content")
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

axe_report_with_no_violations = {
    "violations": []
}

axe_report_with_some_violations = {
    "url": "URL axe is run against",
    "timestamp": "2000-01-01T00:00:00.000Z",
    "violations": [
        "Details of a violation",
        "Details of a different violation"
    ],
    "testEngine": {"version": "0.0.0"}
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
    expected_file_name = "screenshots/2019-02-15_00.00.00.000000_test_screenshot.png"
    assert_that(driver.screenshot_filename, equal_to(expected_file_name),
                "The screenshot filename was incorrect")
    assert_that(result, equal_to(True), "The screenshot should have been saved successfully, and the file name should "
                                        "be returned")
    assert_that(BrowserHandler.saved_screenshot_file_names, has_length(1),
                "Expected there to be one file name in the list of saved files names")
    assert_that(BrowserHandler.saved_screenshot_file_names[0], equal_to(expected_file_name),
                "Expected the saved file name to match the expected string")
    # clean up saved file names
    BrowserHandler.saved_screenshot_file_names = []


@mock.patch("uitestcore.utilities.browser_handler.get_current_datetime",
            side_effect=lambda *args: datetime.strptime("2019-02-15_00.00.00.000000", "%Y-%m-%d_%H.%M.%S.%f"))
def test_take_screenshot_save_file_fail(mock_get_current_datetime):
    driver = MockDriver(1024, 768, 2000, False)

    result = BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called(mock_get_current_datetime)
    assert_that(result, equal_to(False), "The screenshot should have failed to save")
    assert_that(BrowserHandler.saved_screenshot_file_names, has_length(0),
                "Expected there to be nothing in the list of saved file names")
    # clean up saved file names
    BrowserHandler.saved_screenshot_file_names = []


@mock.patch("os.path.exists", side_effect=lambda *args: False)
@mock.patch("os.makedirs")
@mock.patch("uitestcore.utilities.browser_handler.get_current_datetime",
            side_effect=lambda *args: datetime.strptime("2019-02-15_00.00.00.000000", "%Y-%m-%d_%H.%M.%S.%f"))
def test_take_screenshot_save_file_with_invalid_characters(mock_get_current_datetime, mock_makedirs, mock_path_exists):
    driver = MockDriver(1024, 768, 2000)

    BrowserHandler.take_screenshot(driver, "abc://test_screenshot")

    check_mocked_functions_called(mock_path_exists, mock_makedirs, mock_get_current_datetime)
    expected_file_name = "screenshots/2019-02-15_00.00.00.000000_abc__test_screenshot.png"
    assert_that(driver.screenshot_filename, equal_to(expected_file_name),
                "The screenshot filename was incorrect")
    assert_that(BrowserHandler.saved_screenshot_file_names[0], equal_to(expected_file_name),
                "The screenshot filename was incorrect")
    # clean up saved file names
    BrowserHandler.saved_screenshot_file_names = []


@mock.patch("os.path.exists", side_effect=lambda *args: True)
def test_take_screenshot_resize_window(mock_path_exists):
    driver = MockDriver(1024, 768, 2000)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called(mock_path_exists)
    assert_that(driver.num_resizes, equal_to(2), "Window should have been resized for the screenshot and then reset")
    assert_that(driver.window_height, equal_to(768), "Window height should have been reverted to its original value")
    # clean up saved file names
    BrowserHandler.saved_screenshot_file_names = []


@mock.patch("os.path.exists", side_effect=lambda *args: True)
def test_take_screenshot_no_resize_window(mock_path_exists):
    driver = MockDriver(1024, 768, 500)

    BrowserHandler.take_screenshot(driver, "test_screenshot")

    check_mocked_functions_called(mock_path_exists)
    assert_that(driver.num_resizes, equal_to(0), "Window should not have been resized")
    assert_that(driver.window_height, equal_to(768), "Window height should not have changed")
    # clean up saved file names
    BrowserHandler.saved_screenshot_file_names = []


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


@mock.patch("os.listdir", side_effect=lambda *args: ["test1.png", "test2.jpg", "test3.png", "test4.png", "test5.bmp"])
@mock.patch("os.path.exists", side_effect=lambda *args: True)
@mock.patch("shutil.move")
def test_move_screenshots_to_folder_with_file_names(mock_move, mock_path_exists, mock_listdir):
    BrowserHandler.move_screenshots_to_folder("test_folder", ["test2.jpg", "test4.png", "test5.bmp"])

    check_mocked_functions_called(mock_listdir, mock_path_exists, mock_move)
    assert_that(mock_move.call_count, equal_to(3), "Only files passed in to method should be moved")
    mock_move.assert_any_call("screenshots/test2.jpg", "screenshots/test_folder")
    mock_move.assert_any_call("screenshots/test4.png", "screenshots/test_folder")
    mock_move.assert_any_call("screenshots/test5.bmp", "screenshots/test_folder")


def test_take_and_move_screenshots_to_folder():
    # This is more of an integration test, validating the combination of take_screenshot and move_screenshots_to_folder.
    driver = MockDriver(1024, 768, 2000, True)
    driver.save_test_file = True # Set the mock so that it will save a real file.

    # take_screenshot
    result = BrowserHandler.take_screenshot(driver, "test_file_name")
    assert_that(result, equal_to(True), "Expected to successfully save the test file")
    assert_that(BrowserHandler.saved_screenshot_file_names, has_length(1), "Expected to have one saved file name")

    # move_screenshots_to_folder
    file_name = BrowserHandler.saved_screenshot_file_names[0]
    BrowserHandler.move_screenshots_to_folder("test_folder", [file_name])
    expected_moved_file_path = "screenshots/test_folder/" + file_name.split("/")[1]
    assert_that(os.path.exists(expected_moved_file_path),
                "Expected to find the file moved to the test_folder directory")

    # clean up saved file names
    BrowserHandler.saved_screenshot_file_names = []
    # Clean up file that has been created
    os.remove(expected_moved_file_path)


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
def test_start_browserstack(mock_remote, mock_load, mock_browser_handler_open):
    context = MockContext()

    start_browserstack(context)

    check_mocked_functions_called(mock_remote, mock_load, mock_browser_handler_open)
    mock_remote.assert_called_with(command_executor="https://test_user:1234@test_server/wd/hub",
                                   desired_capabilities={"cap1": "1", "cap2": "2", "cap3": "3"})


@mock.patch("axe_selenium_python.Axe.run")
@mock.patch("axe_selenium_python.Axe.inject")
def test_run_axe_accessibility_report_with_no_scenario_name_set(mock_inject, mock_run):
    context = MockContext(scenario_name=None)
    assert_that(context, not_(has_property('scenario_name')),
                "Mocked context should have no scenario_name set")

    BrowserHandler.run_axe_accessibility_report(context)

    assert_that(context.scenario_name, equal_to("No Scenario name passed to function"),
                "Given no scenario_name is set on the mocked context, the scenario name should be set by the function")
    check_mocked_functions_called(mock_inject, mock_run)


@mock.patch("axe_selenium_python.Axe.run")
@mock.patch("axe_selenium_python.Axe.inject")
def test_run_axe_accessibility_report_with_no_element_filter_passed(mock_inject, mock_run):
    context = MockContext(scenario_name="element_filter is not provided in the method call")

    BrowserHandler.run_axe_accessibility_report(context)

    check_mocked_functions_called(mock_inject, mock_run)
    mock_run.assert_called_with(context=None, options=None)


@mock.patch("axe_selenium_python.Axe.run")
@mock.patch("axe_selenium_python.Axe.inject")
def test_run_axe_accessibility_report_with_an_element_filter_passed(mock_inject, mock_run):
    context = MockContext(scenario_name="element_filter is provided in the method call")
    element_filter = {"include": [["#example_element_filter"]]}

    BrowserHandler.run_axe_accessibility_report(context, element_filter=element_filter)

    check_mocked_functions_called(mock_inject, mock_run)
    mock_run.assert_called_with(context=element_filter, options=None)


@mock.patch("axe_selenium_python.Axe.run")
@mock.patch("axe_selenium_python.Axe.inject")
def test_run_axe_accessibility_report_with_no_rule_filter_passed(mock_inject, mock_run):
    context = MockContext(scenario_name="rule_filter is not provided in the method call")

    BrowserHandler.run_axe_accessibility_report(context)

    check_mocked_functions_called(mock_inject, mock_run)
    mock_run.assert_called_with(context=None, options=None)


@mock.patch("axe_selenium_python.Axe.run")
@mock.patch("axe_selenium_python.Axe.inject")
def test_run_axe_accessibility_report_with_a_rule_filter_passed(mock_inject, mock_run):
    context = MockContext(scenario_name="element_filter is provided in the method call")
    rule_filter = {"runOnly": ['wcag2a', 'wcag2aa']}

    BrowserHandler.run_axe_accessibility_report(context, rule_filter=rule_filter)

    check_mocked_functions_called(mock_inject, mock_run)
    mock_run.assert_called_with(context=None, options=rule_filter)


@mock.patch("uitestcore.utilities.browser_handler.write_axe_violations_to_file")
@mock.patch("axe_selenium_python.Axe.run", return_value=axe_report_with_no_violations)
@mock.patch("axe_selenium_python.Axe.inject")
def test_run_axe_accessibility_report_when_axe_report_returns_no_violations(mock_inject, mock_run,
                                                                            mock_write_axe_violations_to_file):
    context = MockContext(scenario_name="axe returns no violations")

    actual_report = BrowserHandler.run_axe_accessibility_report(context)

    check_mocked_functions_called(mock_inject, mock_run)
    check_mocked_functions_not_called(mock_write_axe_violations_to_file)
    assert_that(actual_report, equal_to(axe_report_with_no_violations),
                "Expected an axe report (with no violations) to be returned by 'run_axe_accessibility_report'")


@mock.patch("uitestcore.utilities.browser_handler.write_axe_violations_to_file")
@mock.patch("axe_selenium_python.Axe.run", return_value=axe_report_with_some_violations)
@mock.patch("axe_selenium_python.Axe.inject")
def test_run_axe_accessibility_report_when_axe_report_returns_some_violations(mock_inject, mock_run,
                                                                              mock_write_axe_violations_to_file):
    context = MockContext(scenario_name="axe returns some violations")

    actual_report = BrowserHandler.run_axe_accessibility_report(context)

    check_mocked_functions_called(mock_inject, mock_run, mock_write_axe_violations_to_file)
    mock_write_axe_violations_to_file.assert_called_with(context, axe_report_with_some_violations)
    assert_that(actual_report, equal_to(axe_report_with_some_violations),
                "Expected an axe report (with some violations) to be returned by 'run_axe_accessibility_report'")


@mock.patch("builtins.open", new_callable=mock_open())
def test_write_axe_violations_to_file_writes_expected_content_to_expected_file_location(mock_open_file):
    mock_scenario_name = "testing the method to write to report"
    mock_page_title = "test title"
    mock_browser_name = "test browser name"
    mock_browser_version = "test browser version"
    context = MockContext(scenario_name=mock_scenario_name,
                          axe=MockAxe(selenium=MockSelenium(title=mock_page_title,
                                                            capabilities_browser_name=mock_browser_name,
                                                            capabilities_browser_version=mock_browser_version)))
    expected_report_content_snippets = [mock_scenario_name,
                                        mock_page_title,
                                        mock_browser_name,
                                        mock_browser_version,
                                        axe_report_with_some_violations['url'],
                                        axe_report_with_some_violations['timestamp'],
                                        axe_report_with_some_violations['testEngine']['version']
                                        ] + axe_report_with_some_violations['violations']

    write_axe_violations_to_file(context, axe_report_with_some_violations)

    check_mocked_functions_called(mock_open_file, mock_open_file.return_value.__enter__().write)
    mock_open_file.assert_called_once_with("axe_reports/violations/violations.txt", "a+", encoding="utf-8")

    content_written_to_report = mock_open_file.return_value.__enter__().write.call_args_list[0].args[0]
    for expected_report_content_snippet in expected_report_content_snippets:
        assert_that(content_written_to_report, contains_string(expected_report_content_snippet),
                    f"Expected the snippet of content {expected_report_content_snippet} to be in the report written to "
                    f"the violations.txt file")
