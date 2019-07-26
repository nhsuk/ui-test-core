from hamcrest import assert_that, equal_to

from ui_automation_core.finder import Finder
from ui_automation_core.interrogator import Interrogator


class MockDriver(object):

    def get_cookies(self):
        mock_cookies = [{"name": "nhsuk-cookie-consent", "value": "%7B%22preferences%22%3Atrue%7D"},
                        {"name": "s_getNewRepeat", "value": "1564127000350-Repeat"}]
        return mock_cookies


def test_get_value_from_cookie_with_empty_string():
    finder = Finder("driver", "logger")
    test_finder = Interrogator(MockDriver(), "logger", finder)
    name = ""
    result = test_finder.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_none_value():
    finder = Finder("driver", "logger")
    test_finder = Interrogator(MockDriver(), "logger", finder)
    name = None
    result = test_finder.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_correct_value():
    finder = Finder("driver", "logger")
    test_finder = Interrogator(MockDriver(), "logger", finder)
    name = "nhsuk-cookie-consent"
    result = test_finder.get_value_from_cookie(name)
    assert_that(result, equal_to("%7B%22preferences%22%3Atrue%7D"), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_wrong_key_value():
    finder = Finder("driver", "logger")
    test_finder = Interrogator(MockDriver(), "logger", finder)
    name = "nhsuk-consent"
    result = test_finder.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")






