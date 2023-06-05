from unittest import mock
from unittest.mock import MagicMock
from hamcrest import assert_that, equal_to, contains_exactly
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.unit_test_utils import check_mocked_functions_called
from uitestcore.finder import Finder
from uitestcore.interactor import Interactor
from uitestcore.interrogator import Interrogator
from uitestcore.page_element import PageElement
from uitestcore.waiter import Waiter


class MockFinder:
    def __init__(self, driver=None, logger=None):
        self.driver = driver
        self.logger = logger
        self.mock_element = MockWebElement()

    def element(self, page_element):
        self.mock_element.page_element = page_element
        return self.mock_element


class MockWebElement:
    def __init__(self):
        self.page_element = None
        self.clicked_elements = []
        self.tag_name = "select"
        self.text = ""

    def click(self):
        self.clicked_elements.append(self.page_element)

    @staticmethod
    def get_dom_attribute(*_args):
        return None

    def send_keys(self, value):
        self.text += value

    def clear(self):
        self.text = ""


class MockInterrogator:
    def __init__(self, current_url):
        self.current_url = current_url

    def get_current_url(self):
        return self.current_url


class MockDriver(object):
    def __init__(self, deleted_cookies=None):
        if deleted_cookies is None:
            deleted_cookies = []
        self.deleted_cookies = deleted_cookies
        self.refresh_count = 0

    @staticmethod
    def get_cookies():
        mock_cookies = [{"name": "cookie-consent", "value": "%7B%22preferences%22%3Atrue%7D"},
                        {"name": "s_getNewRepeat", "value": "1564127000350-Repeat"}]
        return mock_cookies

    def delete_cookie(self, cookie_name):
        self.deleted_cookies.append(cookie_name)

    def refresh(self):
        self.refresh_count += 1


def test_click_element():
    find = MockFinder()
    interact = Interactor(None, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")

    interact.click_element(page_element)

    assert_that(len(find.mock_element.clicked_elements), equal_to(1), "The element should have been clicked once")
    assert_that(find.mock_element.clicked_elements[0], equal_to(page_element), "Incorrect element clicked")


def test_execute_click_with_java_script():
    mock_driver = MagicMock(name="driver")
    find = MockFinder()
    interact = Interactor(mock_driver, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")

    interact.execute_click_with_java_script(page_element)

    mock_driver.execute_script.assert_called_once_with("arguments[0].click();", find.mock_element)


@mock.patch("selenium.webdriver.support.select.Select.select_by_visible_text")
def test_select_by_visible_text(mock_select_by_visible_text):
    find = MockFinder()
    interact = Interactor(None, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")

    interact.select_by_visible_text(page_element, "text to check")

    mock_select_by_visible_text.assert_called_once_with("text to check")


@mock.patch("selenium.webdriver.support.select.Select.select_by_value")
def test_select_by_value(mock_select_by_value):
    find = MockFinder()
    interact = Interactor(None, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")

    interact.select_by_value(page_element, "value to check")

    mock_select_by_value.assert_called_once_with("value to check")


@mock.patch("selenium.webdriver.support.select.Select.select_by_index")
def test_select_by_index(mock_select_by_index):
    find = MockFinder()
    interact = Interactor(None, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")

    interact.select_by_index(page_element, "index to check")

    mock_select_by_index.assert_called_once_with("index to check")


def test_enter_text():
    find = MockFinder()
    interact = Interactor(None, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")

    interact.enter_text(page_element, "abcd", False)

    assert_that(find.mock_element.text, equal_to("abcd"), "Text not sent to element correctly")


def test_enter_text_clears_first():
    find = MockFinder()
    interact = Interactor(None, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")
    find.mock_element.text = "1234"

    interact.enter_text(page_element, "abcd", True)

    assert_that(find.mock_element.text, equal_to("abcd"), "Text not cleared before sending")


def test_send_keys():
    find = MockFinder()
    interact = Interactor(None, find, None, None, None)
    page_element = PageElement(By.ID, "test-id")

    interact.send_keys(page_element, Keys.ARROW_LEFT)

    assert_that(find.mock_element.text, equal_to(""), "Key not sent to element correctly")


def test_open_url():
    mock_driver = MagicMock(name="driver")
    mock_waiter = MagicMock(name="wait")
    interact = Interactor(mock_driver, None, None, mock_waiter, MagicMock(name="log"))

    interact.open_url("test/url")

    mock_driver.get.assert_called_once_with("test/url")
    mock_waiter.for_page_to_load.assert_called_once()


def test_append_and_open_url():
    mock_driver = MagicMock(name="driver")
    mock_waiter = MagicMock(name="wait")
    interact = Interactor(mock_driver, None, MockInterrogator("test/url"), mock_waiter, MagicMock(name="log"))

    interact.append_and_open_url("/extra")

    mock_driver.get.assert_called_once_with("test/url/extra")


def test_close_current_window_switch_to_a_remaining_window():
    mock_driver = MagicMock(name="driver")
    mock_driver.window_handles = ["window_0", "window_1"]
    mock_driver.current_window_handle = "window_1"
    interact = Interactor(mock_driver, None, None, None, None)

    interact.close_current_window()

    mock_driver.close.assert_called_once()
    mock_driver.switch_to.window.assert_called_once_with("window_0")


def test_close_current_window_switch_to_next_window():
    mock_driver = MagicMock(name="driver")
    mock_driver.window_handles = ["window_0", "window_1"]
    mock_driver.current_window_handle = "window_0"
    interact = Interactor(mock_driver, None, None, None, None)

    interact.close_current_window()

    mock_driver.close.assert_called_once()
    mock_driver.switch_to.window.assert_called_once_with("window_1")


def test_close_current_window_with_one_window():
    mock_driver = MagicMock(name="driver")
    mock_driver.window_handles = ["window_0"]
    mock_driver.current_window_handle = "window_0"
    interact = Interactor(mock_driver, None, None, None, None)

    interact.close_current_window()

    mock_driver.close.assert_called_once()
    mock_driver.switch_to.window.assert_not_called()


def test_scroll_into_view():
    mock_driver = MagicMock(name="driver")
    find = MockFinder()
    interact = Interactor(mock_driver, find, None, None, MagicMock(name="log"))
    page_element = PageElement(By.ID, "test-id")

    interact.scroll_into_view(page_element)

    mock_driver.execute_script.assert_called_once_with("arguments[0].scrollIntoView();", find.mock_element)


def test_switch_to_next_window():
    mock_driver = MagicMock(name="driver")
    mock_driver.window_handles = ["window_0", "window_1"]
    interact = Interactor(mock_driver, None, None, None, MagicMock(name="log"))

    interact.switch_to_next_window()

    mock_driver.switch_to.window.assert_called_once_with("window_1")


def test_switch_to_original_window():
    mock_driver = MagicMock(name="driver")
    mock_driver.window_handles = ["window_0", "window_1"]
    interact = Interactor(mock_driver, None, None, None, None)

    interact.switch_to_original_window()

    mock_driver.switch_to.window.assert_called_once_with("window_0")


def test_switch_to_frame():
    mock_driver = MagicMock(name="driver")
    finder = Finder(mock_driver, MagicMock(name="logger"))
    interrogator = Interrogator(mock_driver, finder, "logger")
    waiter = Waiter(mock_driver, finder, "logger")
    test_interactor = Interactor(mock_driver, finder, interrogator, waiter, "logger")
    frame_to_find = PageElement(By.ID, "frame_id")

    test_interactor.switch_to_frame(frame_to_find)

    mock_driver.switch_to.frame.assert_called_once_with(finder.element(frame_to_find))


def test_accept_alert():
    mock_driver = MagicMock(name="driver")
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, finder, "logger")
    waiter = Waiter(mock_driver, finder, "logger")
    test_interactor = Interactor(mock_driver, finder, interrogator, waiter, "logger")

    test_interactor.accept_alert()

    mock_driver.switch_to.alert.accept.assert_called_once()


def test_dismiss_alert():
    mock_driver = MagicMock(name="driver")
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, finder, "logger")
    waiter = Waiter(mock_driver, finder, "logger")
    test_interactor = Interactor(mock_driver, finder, interrogator, waiter, "logger")
    mock_driver.switch_to.alert.dismiss = MagicMock(name="dismiss")

    test_interactor.dismiss_alert()

    mock_driver.switch_to.alert.dismiss.assert_called_once()


def test_enter_text_into_alert():
    mock_driver = MagicMock(name="driver")
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, finder, "logger")
    waiter = Waiter(mock_driver, finder, "logger")
    test_interactor = Interactor(mock_driver, finder, interrogator, waiter, "logger")
    text = "my text value"

    test_interactor.enter_text_into_alert(text)

    mock_driver.switch_to.alert.send_keys.assert_called_once_with(text)


def test_switch_to_default_content():
    mock_driver = MagicMock(name="driver")
    interact = Interactor(mock_driver, None, None, None, None)

    interact.switch_to_default_content()

    check_mocked_functions_called(mock_driver.switch_to.default_content)


def test_clear_cookie_and_refresh_page_deletes_the_cookie():
    driver = MockDriver()
    interact = Interactor(driver, None, None, None, None)
    name = "Banner717"
    interact.clear_cookie_and_refresh_page(name)
    assert_that(driver.deleted_cookies, contains_exactly("Banner717"), "The cookie should be deleted")


def test_clear_cookie_and_refresh_page_performs_a_refresh():
    driver = MockDriver()
    interact = Interactor(driver, None, None, None, None)
    name = "Banner717"
    interact.clear_cookie_and_refresh_page(name)
    assert_that(driver.refresh_count, equal_to(1), "The cookie should be refreshed once")


def test_clear_all_cookies():
    driver = MagicMock()
    interact = Interactor(driver, None, None, None, None)

    interact.clear_all_cookies()

    driver.delete_all_cookies.assert_called_once()
