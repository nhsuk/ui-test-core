from hamcrest import assert_that, equal_to, contains

from uitestcore.finder import Finder
from uitestcore.interrogator import Interrogator


class MockDriver(object):

    def __init__(self, deleted_cookies=[]):
        self.deleted_cookies = deleted_cookies
        self.refresh_count = 0

    def get_cookies(self):
        mock_cookies = [{"name": "nhsuk-cookie-consent", "value": "%7B%22preferences%22%3Atrue%7D"},
                        {"name": "s_getNewRepeat", "value": "1564127000350-Repeat"}]
        return mock_cookies

    def delete_cookie(self, cookie_name):
        self.deleted_cookies.append(cookie_name)

    def refresh(self):
        self.refresh_count += 1


def test_get_value_from_cookie_with_empty_string():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), "logger", finder)
    name = ""
    result = test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_none_value():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), "logger", finder)
    name = None
    result =  test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_correct_value():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), "logger", finder)
    name = "nhsuk-cookie-consent"
    result = test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to("%7B%22preferences%22%3Atrue%7D"), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_wrong_key_value():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), "logger", finder)
    name = "nhsuk-consent"
    result = test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_clear_cookie_and_refresh_page_deletes_the_cookie():
    finder = Finder("driver", "logger")
    driver = MockDriver()
    test_interrogator = Interrogator(driver, "logger", finder)
    name = "Banner717"
    test_interrogator.clear_cookie_and_refresh_page(name)
    assert_that(driver.deleted_cookies, contains("Banner717"), "The cookie should be deleted")


def test_clear_cookie_and_refresh_page_performs_a_refresh():
    finder = Finder("driver", "logger")
    driver = MockDriver()
    test_interrogator = Interrogator(driver, "logger", finder)
    name = "Banner717"
    test_interrogator.clear_cookie_and_refresh_page(name)
    assert_that(driver.refresh_count, equal_to(1), "The cookie  should be refreshed once")
