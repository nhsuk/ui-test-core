from hamcrest import assert_that, equal_to
from uitestcore.custom_expected_conditions import *


class MockDriver:
    def __init__(self, state):
        self.state = state

    def execute_script(self, _script):
        return self.state


class MockFinder:
    @staticmethod
    def elements(page_element):
        if page_element:
            return [MockElement("valid_attribute")]
        return None


class MockElement:
    def __init__(self, attribute):
        self.attribute = attribute

    def get_attribute(self, *_args):
        return self.attribute


def test_browser_is_ready_complete():
    inst = BrowserIsReady()

    result = inst(MockDriver("complete"))

    assert_that(result, equal_to(True), "The browser should have been ready")


def test_browser_is_ready_incomplete():
    inst = BrowserIsReady()

    result = inst(MockDriver("incomplete"))

    assert_that(result, equal_to(False), "The browser should not have been ready")


def test_browser_is_ready_none():
    inst = BrowserIsReady()

    result = inst(MockDriver(None))

    assert_that(result, equal_to(False), "The browser should not have been ready")


def test_element_has_attribute():
    inst = ElementHasAttribute(MockFinder(), "page_element", "test_name", "valid_attribute")

    result = inst("driver")

    assert_that(result, equal_to(True), "The attribute should have been found")


def test_element_has_attribute_no_element():
    inst = ElementHasAttribute(MockFinder(), None, "test_name", "valid_attribute")

    result = inst("driver")

    assert_that(result, equal_to(False), "The attribute should not have been found")


def test_element_has_attribute_not_matching():
    inst = ElementHasAttribute(MockFinder(), "page_element", "test_name", "invalid_attribute")

    result = inst("driver")

    assert_that(result, equal_to(False), "The attribute should not have been found")
